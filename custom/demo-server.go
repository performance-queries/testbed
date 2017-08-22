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
	// Location of generated graph
	Output string
	// The command to run for the collector.
	CollectorCmd []string
}

var perPacketQuery = Query{
	Name:         "Per Packet Queueing Latencies",
	Graph:        true,
	Switch:       9090,
	File:         "per_packet_query/per_packet_queue_lengths.json",
	Output:       "packet_qlens.png",
	CollectorCmd: []string{"./record_register_continuous.sh", "1024", "qlens", "times"},
}

var perFlowQuery = Query{
	Name:         "Flow statistics",
	Graph:        false,
	Switch:       9090,
	File:         "per_flow_query/per_flow_bursts.json",
	Output:       "per_flow.txt",
	CollectorCmd: []string{"./demo_5tuple_record_registers.sh"},
}

// Impelemnts http.Handler
type DemoHandler struct {
	// The current running query, along with all the collectors.
	cmds []*exec.Cmd
}

func cleanupFiles() {
	os.Remove("data/latency.png")
	os.Remove("data/qlens_series_full.png")
	os.Remove("data/qlens_series_latest.png")
	os.Remove("data/flow_stats.html")
}

func (h *DemoHandler) stopQuery() error {
	for _, cmd := range h.cmds {
		if cmd != nil && cmd.Process != nil {
			syscall.Kill(-cmd.Process.Pid, syscall.SIGKILL)
			cmd.Wait()
		}
	}
	// Cleanup mininet
	out, err := exec.Command("/usr/local/bin/mn", "-c").Output()
	fmt.Println(string(out))
	h.cmds = []*exec.Cmd{}
	fmt.Printf("Query stopped...")
	cleanupFiles()
	fmt.Println("Files cleaned up.")
	return err
}

func (h *DemoHandler) runSwitch(jf string) {
	// Launch the switch in the background
	cmd := exec.Command("./run_demo.sh", jf)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	// Need this so the child process has a separate process group ID.
	// Then we can kill it from this program. If it had the same PGID,
	// the kill command usually kills itself first. womp.
	cmd.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}
	h.cmds = append(h.cmds, cmd)
	cmd.Start()

	fmt.Printf("Started command at path %s", cmd.Path)
	fmt.Printf("Process details: %+v", cmd.Process)
}

func (h *DemoHandler) launchCollector(args []string) *exec.Cmd {
	cmd := exec.Command(args[0], args[1:]...)
	cmd.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	h.cmds = append(h.cmds, cmd)
	return cmd
}

func (h *DemoHandler) launchCollectors(q Query) {
	cmd1 := h.launchCollector([]string{"./record_latency_continuous.sh"})
	var cmd2 *exec.Cmd
	if len(q.CollectorCmd) > 0 {
		cmd2 = h.launchCollector(q.CollectorCmd)
	}
	cmd1.Start()
	if cmd2 != nil {
		cmd2.Start()
	}
}

func (h *DemoHandler) startQuery(q Query) error {
	if len(h.cmds) > 0 {
		// This means the previous query hasn't yet terminated.
		return fmt.Errorf("Previous query has not been terminated")
	}
	// Launch switch in the background
	h.runSwitch(q.File)
	// Launch collector in the background. The collector
	// updates the graphs.
	h.launchCollectors(q)
	fmt.Println("Launched mininet demo")
	return nil
}

func (h *DemoHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Serving Query")
	/*if r.Method != "POST" {
		http.NotFound(w, r)
	}*/
	params := r.URL.Query()
	queryType := ""
	if len(params["type"]) != 0 {
		queryType = params["type"][0]
	}
	var query Query
	var err error
	switch queryType {
	case "flow":
		err = h.startQuery(perFlowQuery)
	case "packet":
		err = h.startQuery(perPacketQuery)
	case "stop":
		err = h.stopQuery()
	default:
		// Just run the plain switch if it's not already running
		if len(h.cmds) == 0 {
			h.runSwitch(perFlowQuery.File)
			cmd1 := h.launchCollector([]string{"./record_latency_continuous.sh"})
			cmd1.Start()
		}
	}
	// Report an error to the client
	if err != nil {
		w.WriteHeader(500)
		io.WriteString(w, err.Error())
		return
	}
	// Otherwise, return the location to the graph or table of the query output.
	io.WriteString(w, query.Output)
}

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
