use std::io;

pub fn poll_readiness(fd: i32, timeout_ms: u64) -> io::Result<bool> {
    let mut pollfd = libc::pollfd { fd, events: libc::POLLIN, revents: 0 };
    let ret = unsafe { libc::poll(&mut pollfd, 1, timeout_ms as i32) };
    if ret < 0 { return Err(io::Error::last_os_error()); }
    Ok(ret > 0)
}