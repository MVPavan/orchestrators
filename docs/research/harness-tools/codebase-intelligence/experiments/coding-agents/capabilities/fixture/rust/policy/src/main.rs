use fixture_policy::{evaluate, StrictPolicy};
use std::io::{self, BufRead};

fn main() {
    let policy = StrictPolicy::new("BLOCKED");
    for line in io::stdin().lock().lines() {
        let input = line.unwrap_or_default();
        let response = match input.strip_prefix("fixture-policy-v1|") {
            Some(actor) if !actor.contains('|') => evaluate(&policy, actor),
            _ => "error",
        };
        println!("fixture-policy-v1|{response}");
    }
}
