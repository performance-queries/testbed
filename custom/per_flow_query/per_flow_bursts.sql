def flow_stats ([last_time, total_size, total_time, num_bursts], [tin]):
  delta = 800000;
  if (tin - last_time > delta) {
    num_bursts = num_bursts + 1;
  } else {
    total_time = total_time + tin - last_time;
  }
  total_size = total_size + 1;
  last_time = tin

result = groupby(T, [srcip, dstip, srcport, dstport, proto, switch], flow_stats);
