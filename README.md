# Veridonia Simulation

This repository contains a simulation of the Veridonia content curation system. The simulation implements a community-driven multi-stage voting process paired with an ELO-based reputation system. It is inspired by the system described in the Veridonia whitepaper. Some differences in implementation exist to better suit the simulation environment.

## Overview

Veridonia is designed to improve online content curation by promoting transparency, meritocracy, and community governance. Instead of relying on opaque, engagement-driven algorithms, Veridonia leverages a multi-stage voting mechanism and dynamic reputation adjustments to evaluate content quality.

In this simulation:

- **Users** are modeled with a baseline ELO rating (default of 800) and a "goodness" factor, which influences their voting behavior.
- **Posts** have a quality score between 0 and 1.
- A **multi-stage voting process** determines whether a post is upvoted or downvoted, with users selected based on their ELO ratings.
- A **special stage** allows low-ELO users (elo ≤ 800) to vote without affecting the overall decision, though their ELO is still adjusted.
- The simulation also features a growing user population, mimicking a realistic social platform environment.

## Features

- **User Modeling:** Each user has attributes including ELO, goodness, mood factor, and a vote count.
- **Voting Mechanism:** Users vote on posts based on a combination of their adjusted goodness (affected by mood) and the quality of the post.
- **Multi-Stage Voting:**
  - For populations with fewer than 20 high-ELO users, a single stage of voting is performed.
  - For larger populations, a two-stage process is used:
    - **Stage 1:** A sample from the lower ELO tier (bottom 70%) votes.
    - **Stage 2:** If the first stage decision is positive (upvote), a sample from the upper ELO tier (top 30%) is used to validate the decision.
  - **Special Stage:** Low-ELO users (≤ 800) vote separately, and their votes are used only to adjust their own ELO scores.
- **ELO Adjustments:** User ratings are updated based on vote outcomes using team-based ELO updates.
- **Visualization:** After simulation runs, various plots display distributions of user goodness, ELO ratings, voting accuracy over time, population growth, vote ratios, and sample sizes.

## Dependencies

The simulation requires the following Python packages:

- Python 3.x
- [NumPy](https://numpy.org/)
- [Matplotlib](https://matplotlib.org/)
- [termcolor](https://pypi.org/project/termcolor/)
- [tqdm](https://tqdm.github.io/)
- [SciPy](https://www.scipy.org/) (for statistical functions)

You can install the required packages using pip:

```bash
pip install numpy matplotlib termcolor tqdm scipy
```

## How to Run the Simulation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/veridonia-simulation.git
   cd veridonia-simulation
   ```

2. **Run the Simulation Script:**

   The simulation is implemented in `simulation.py`. To run the simulation, simply execute:

   ```bash
   python simulation.py
   ```

   This will:

   - Grow the user population gradually until it reaches 10,000 users.
   - Generate posts and simulate the multi-stage voting process.
   - Update users' ELO ratings based on voting accuracy.
   - Display various visualizations of the simulation data.

## Acknowledgements

This simulation is a proof-of-concept implementation based on the principles outlined in the Veridonia whitepaper. It aims to explore the potential of community-driven content curation and transparent reputation systems. Please refer to the whitepaper for the complete theoretical framework.

---

Feel free to contribute, report issues, or suggest improvements by opening an issue or pull request in the repository.

Happy simulating!
