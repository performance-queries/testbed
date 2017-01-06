use std::net::UdpSocket;
use std::thread;
use std::time;

fn main() {
  let socket = UdpSocket::bind("127.0.0.1:3000").unwrap();
  let ten_millis = time::Duration::from_millis(10);
  loop {
    thread::sleep(ten_millis);
    let _ = socket.send_to(&['a' as u8;350], "127.0.0.1:4000");
  }
}
