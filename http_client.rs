use std::io::prelude::*;
use std::net::TcpStream;
use std::str;

fn main() {
    let mut stream = TcpStream::connect("127.0.0.1:80").unwrap();

    // _ ignores the result
    let _ = stream.write(b"GET /loremipsum.txt\r\n");

    // mutable array with 3000 elements, each initialized to zero
    let mut result = [0; 3000];

    // &mut result creates a mutable slice with all elements
    // mut indicates that it can be mutated
    let _ = stream.read(&mut result);

    print!("{}", str::from_utf8(&result).unwrap());
}
