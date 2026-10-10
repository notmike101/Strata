// Extracted from current src/core/verify.cpp before edits.
bool capture_self_commit(int T,bool batch,bool enabled,bool qfuse) { return T == 1 && !batch && !qfuse && enabled; }
bool skip_commit(int T,bool batch,bool enabled,bool qfuse) { return T == 1 && enabled; }
