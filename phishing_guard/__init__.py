"""Phishing Guard and Coach: a two-agent assistant for an employee's inbox.

Modules:
    config        API key loading, model name, tracing switch
    world         mock mailbox, users, threat intel, logs, reset_world()
    classifier    TF-IDF + logistic regression training, loading, top_words()
    tools         function tools Guard can call
    guard_agents  Guard (and later Coach) agent definitions, build_input()
    trace_utils   show_trace() copied from the class tutorial
"""
