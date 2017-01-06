use std::net::UdpSocket;
use std::thread;
use std::time;
extern crate rand;

fn main() {
  let socket = UdpSocket::bind("127.0.0.1:3000").unwrap();
  loop {
    thread::sleep(time::Duration::from_millis(rand::random::<u8>() as u64));
    let _ = socket.send_to(&['a' as u8;350], "127.0.0.1:4000");
  }
}
