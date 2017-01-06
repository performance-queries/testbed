use std::io::prelude::*;
use std::net::TcpStream;
use std::str;

fn main() {
    let mut stream = TcpStream::connect("127.0.0.1:80").unwrap();

    // _ ignores the result
    // use as_bytes to go from &str to &[u8]
    // http://stackoverflow.com/questions/23850486/how-do-i-convert-a-string-into-a-vector-of-bytes-in-rust
    let _ = stream.write("GET /loremipsum.txt\r\n".as_bytes());

    // mutable array with 3500 elements, each initialized to zero
    let mut result = [0; 3500];

    // &mut result creates a mutable slice with all elements
    // mut indicates that it can be mutated
    let _ = stream.read(&mut result);

    // get an "& str" from a utf8 array
    print!("{}", str::from_utf8(&result).unwrap());
}
