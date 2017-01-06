use std::net::UdpSocket;

fn main() {
  let socket = UdpSocket::bind("127.0.0.1:3000").unwrap();
  let _ = socket.send_to(&['a' as u8;3500], "127.0.0.1:4000");
}
