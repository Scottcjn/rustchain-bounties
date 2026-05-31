use std::sync::mpsc;
use std::sync::{Arc, atomic::{AtomicUsize, Ordering}};

pub struct BackpressureChannel<T> {
    sender: mpsc::Sender<T>,
    receiver: mpsc::Receiver<T>,
    capacity: Arc<AtomicUsize>,
}

impl<T> BackpressureChannel<T> {
    pub fn new(max: usize) -> (Self, mpsc::Sender<T>) {
        let (tx, rx) = mpsc::channel();
        let cap = Arc::new(AtomicUsize::new(max));
        (Self { sender: tx.clone(), receiver: rx, capacity: cap }, tx)
    }
    pub fn send(&self, msg: T) -> Result<(), mpsc::SendError<T>> {
        let cap = self.capacity.load(Ordering::Relaxed);
        if cap == 0 { return Err(mpsc::SendError(msg)); }
        self.capacity.fetch_sub(1, Ordering::SeqCst);
        self.sender.send(msg)
    }
    pub fn recv(&self) -> Result<T, mpsc::RecvError> {
        let result = self.receiver.recv();
        self.capacity.fetch_add(1, Ordering::SeqCst);
        result
    }
}