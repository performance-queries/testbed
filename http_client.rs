use std::io::prelude::*;
use std::net::TcpStream;
use std::str;
use std::time::SystemTime;

fn main() {
    // If connect doesn't work, unwrap() will throw an exception
    let mut stream = TcpStream::connect("127.0.0.1:80").unwrap();

    // mutable array with 3500 elements, each initialized to zero
    let mut result = [0; 3500];

    loop {
      // Track time of GET
      let now = SystemTime::now();

      // _ ignores the result
      // use as_bytes to go from &str to &[u8]
      // http://stackoverflow.com/questions/23850486/how-do-i-convert-a-string-into-a-vector-of-bytes-in-rust
      let _ = stream.write("GET /loremipsum.txt\r\n".as_bytes());

      // &mut result creates a mutable slice with all elements
      // mut indicates that it can be mutated
      let _ = stream.read(&mut result);

      // print elapsed time
      match now.elapsed() {
        Ok(elapsed) => {
          // it prints '2'
          let get_time = (1000 * elapsed.as_secs()) +
                         (((elapsed.subsec_nanos())/ 1000000) as u64);
          println!("GET time in ms:{}", get_time);
        }
        Err(e) => {
          // an error occured!
          println!("Error: {:?}", e);
        }
      }
    }
    // get an "& str" from a utf8 array
    // if there are non-text characters in result, unwrap() will throw an exception
    // print!("{}", str::from_utf8(&result).unwrap());
}
