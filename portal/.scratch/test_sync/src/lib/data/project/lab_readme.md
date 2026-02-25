# Lineum Core Laboratory

This directory is dedicated to **non-binding hypothesis testing**. 

## Laboratory Protocol

As per Section 4 of the project rules (`.agent/rules.md`), all work in this folder follows these conventions:

1. **Experimental Nature**: Code and configurations in `lab/` are for testing ideas and are NOT part of the audited core production system.
2. **Hypothesis Sources**: 
   - `todo.md`: Contains pending ideas and research targets.
   - `whitepaper-old/`: Legacy documentation that may contain useful leads but is functionally obsolete.
3. **Canonical Sources of Truth**: 
   - `whitepapers/`: Use the latest whitepaper here for binding technical specifications.
   - `output_wp/`: Refer to the latest audit run results for verified system state and metrics.

## Usage

When initiating a new laboratory session (even in a separate thread), ensure the agent is aware of this protocol to maintain consistency between exploratory research and audited implementation.
