use std::io::prelude::*;
use std::net::TcpStream;
use std::str;

fn main() {
    let mut stream = TcpStream::connect("127.0.0.1:80").unwrap();

    // ignore the Result
    let _ = stream.write(b"GET /loremipsum.txt\r\n");

    let mut result = [0; 3000];
    let _ = stream.read(&mut result[..]); // ignore here too
    print!("{}", str::from_utf8(&result).unwrap());
}
