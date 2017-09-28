package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"syscall"
)

const queryAlreadyRunningErrStr = "Another query is currently running. Please press STOP to terminate the current query before running a new one."

var defaultDemoHandler = &DemoHandler{}

var noCacheHeaders = map[string]string{
	"Cache-Control":   "no-cache, private, max-age=0",
	"Pragma":          "no-cache",
	"X-Accel-Expires": "0",
}

// A generic struct containing all info needed for a query.
type Query struct {
	Name string
	// If not graph, then it's a table. Used to determine how display the result.
	Graph bool
	// Thrift port of the switch the query should be run on.
	Switch int
	// JSON file for the compiled query.
	File string
	// The commands to run for the collector.
	CollectorCmds []string
}

// Runs just the mininet topology with latency measurements.
var basicQuery = Query{
	Name:   "Basic Latency Measurement",
	Graph:  true,
	Switch: 909,
	File:   "per_flow_query/per_flow_bursts.json",
	CollectorCmds: []string{
		"./record_latency_continuous.sh",
	},
}

// Runs the mininet topology with the per-packet query.
var perPacketQuery = Query{
	Name:   "Per Packet Queueing Latencies",
	Graph:  true,
	Switch: 9090,
	File:   "per_packet_query/per_packet_queue_lengths.json",
	CollectorCmds: []string{
		"./record_latency_continuous.sh",
		"./record_register_continuous.sh 9090 10000 qlens times",
		"./record_register_continuous.sh 9091 10000 qlens times",
	},
}

// Runs the mininet topology with the per-flow query.
var perFlowQuery = Query{
	Name:   "Flow statistics",
	Graph:  false,
	Switch: 9090,
	File:   "per_flow_query/per_flow_bursts.json",
	CollectorCmds: []string{
		"./record_latency_continuous.sh",
		"./demo_5tuple_record_registers.sh",
	},
}

// Impelemnts http.Handler
type DemoHandler struct {
	// The current running query, along with all the collectors.
	cmds []*exec.Cmd
	// Poor man's mutex to make sure multiple queries don't run simultaneously.
	// TODO(vikram): Fix before publishing.
	queryRunning bool
}

func cleanupFiles() {
	os.Remove("data/latency.png")
	os.Remove("data/qlens_series_full_9090.png")
	os.Remove("data/qlens_series_full_9091.png")
	os.Remove("data/qlens_series_latest.png")
	os.Remove("data/flow_stats.html")
}

// Cleans up the mininet environment, and blocks for its completion.
func cleanupMininet() {
	out, _ := exec.Command("/usr/local/bin/mn", "-c").Output()
	fmt.Println(string(out))
}

func (h *DemoHandler) stopQuery() {
	for _, cmd := range h.cmds {
		if cmd != nil && cmd.Process != nil {
			// Issue a KILL command to the entire process group, which will also
			// kill all spawned children processes.
			syscall.Kill(-cmd.Process.Pid, syscall.SIGKILL)
			cmd.Wait()
		}
	}
	cleanupMininet()
	// Clear the command list.
	h.cmds = []*exec.Cmd{}
	fmt.Printf("Query stopped...")
	// Remove generated data files, so that no stale images are leaked.
	cleanupFiles()
	fmt.Println("Files cleaned up.")
	// We are ready to take another query.
	h.queryRunning = false
}

// Launches a command in the background and records it
// so that it may be killed later.
// Stdout and Stderr are piped into standard out/err.
func (h *DemoHandler) launchCommand(command string) {
	args := strings.Split(command, " ")
	cmd := exec.Command(args[0], args[1:]...)
	// Need this so the child process has a separate process group ID.
	// Then we can kill it from this program. If it had the same PGID,
	// the kill command usually kills itself first. womp.
	cmd.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	h.cmds = append(h.cmds, cmd)
	cmd.Start()
}

// Run the switch in the background.
func (h *DemoHandler) runSwitch(jf string) {
	h.launchCommand("./run_demo.sh " + jf)
}

// Run all measurement collectors in the background.
func (h *DemoHandler) launchCollectors(collectors []string) {
	for _, col := range collectors {
		h.launchCommand(col)
	}
}

// Given a query, runs the mininet topology and collectors
// in the background, while closing the server off to further
// queries.
func (h *DemoHandler) startQuery(q Query) error {
	if h.queryRunning {
		return fmt.Errorf(queryAlreadyRunningErrStr)
	}
	h.queryRunning = true
	h.runSwitch(q.File)
	h.launchCollectors(q.CollectorCmds)
	return nil
}

// Serve the non-static requests, i.e. those that start / stop queries.
func (h *DemoHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	// We will only accept POSTs by convention.
	if r.Method != "POST" {
		http.NotFound(w, r)
		return
	}
	// The URL path should be of the form: .../query?type=X
	params := r.URL.Query()
	queryType := ""
	if len(params["type"]) != 0 {
		queryType = params["type"][0]
	}
	var err error
	switch queryType {
	case "flow":
		err = h.startQuery(perFlowQuery)
	case "packet":
		err = h.startQuery(perPacketQuery)
	case "stop":
		h.stopQuery()
	default:
		err = h.startQuery(basicQuery)
	}
	// Report an error to the client
	if err != nil {
		w.WriteHeader(500)
		io.WriteString(w, err.Error())
		return
	}
	io.WriteString(w, "Success")
}

// Serves static files like images, static html, etc.
func handleData(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("Serving file %s\n", r.URL.Path)
	path := strings.Trim(r.URL.Path, "/")
	http.ServeFile(w, r, "data/"+path)
	for k, v := range noCacheHeaders {
		w.Header().Set(k, v)
	}
}

func main() {
	http.Handle("/query", defaultDemoHandler)
	http.HandleFunc("/", handleData)
	fmt.Println("Serving HTTP traffic on :8000")
	http.ListenAndServe(":8000", nil)
}
