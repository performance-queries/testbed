use std::net::UdpSocket;
use std::thread;
use std::time;
extern crate rand;
use rand::distributions::{IndependentSample, Range};

fn main() {
  let off_time_range = Range::new(1, 999);
  let socket = UdpSocket::bind("127.0.0.1:3000").unwrap();
  let mut rng = rand::thread_rng();
  loop {
    let sleep_duration = time::Duration::from_millis(off_time_range.ind_sample(&mut rng));
    println!("Sleeping for {} ms", sleep_duration.subsec_nanos() / 1000000);
    thread::sleep(sleep_duration);
    let _ = socket.send_to(&['a' as u8;350], "127.0.0.1:4000");
  }
}
