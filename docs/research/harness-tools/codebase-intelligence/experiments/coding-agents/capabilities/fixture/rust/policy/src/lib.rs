pub trait Policy {
    fn authorize(&self, actor: &str) -> Result<bool, PolicyError>;
}

#[derive(Debug)]
pub enum PolicyError {
    EmptyActor,
}

pub struct StrictPolicy {
    blocked_prefix: String,
}

impl StrictPolicy {
    pub fn new(blocked_prefix: &str) -> Self {
        Self {
            blocked_prefix: blocked_prefix.to_owned(),
        }
    }
}

impl Policy for StrictPolicy {
    fn authorize(&self, actor: &str) -> Result<bool, PolicyError> {
        if actor.is_empty() {
            return Err(PolicyError::EmptyActor);
        }
        Ok(!actor.starts_with(&self.blocked_prefix))
    }
}

pub fn evaluate<P: Policy>(policy: &P, actor: &str) -> &'static str {
    match policy.authorize(actor) {
        Ok(true) => "allow",
        Ok(false) | Err(_) => "deny",
    }
}
