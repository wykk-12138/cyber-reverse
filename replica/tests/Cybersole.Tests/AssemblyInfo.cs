using Xunit;

// R206: the suite launches a real Chromium for every browser-backed test, and xunit's default is one collection per
// class running in parallel across all 32 logical cores. Under that load two failures appeared that had nothing to do
// with the product: a CDP WebSocket dropped mid-measurement ("The remote party closed the WebSocket connection"), and
// Avalonia answered "Operations that change non-concurrent collections must have exclusive access" when two headless
// views were built at once.
//
// Four threads still finishes the fast suite in ~20 s and caps peak Chromium instances at four (~1 GB), which matters
// on a machine that has already been pushed into swap once by running this suite beside IDA Pro.
[assembly: CollectionBehavior(MaxParallelThreads = 4)]
