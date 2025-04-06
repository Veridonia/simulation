# Veridonia Simulation

This repository contains a simulation of the Veridonia content curation system. The simulation implements a community-driven multi-stage voting process paired with an ELO-based reputation system. It is based on the principles outlined in the [Veridonia Whitepaper](Whitepaper.md) included in this repository. Some differences in implementation exist to better suit the simulation environment.

## Overview

Veridonia is designed to improve online content curation by promoting transparency, meritocracy, and community governance. Instead of relying on opaque, engagement-driven algorithms that fuel sensationalism and misinformation, Veridonia leverages a multi-stage voting mechanism and dynamic reputation adjustments to evaluate content quality.

In this simulation:

- **Users** are modeled with a baseline ELO rating (default of 800) and a "goodness" factor, which influences their voting behavior.
- **Posts** have a quality score between 0 and 1, with each user creating approximately 2 posts.
- A **multi-stage voting process** determines whether a post is upvoted or downvoted, with users selected based on their ELO ratings.
- A **special stage** allows low-ELO users (elo ≤ 800) to vote without affecting the overall decision, though their ELO is still adjusted.
- The simulation features a growing user population up to 5,000 users, mimicking a realistic social platform environment.
- A **population sample voting** mechanism provides an alternative voting approach using statistically significant samples.

## Features

- **User Modeling:** Each user has attributes including ELO, goodness, mood factor, and a vote count.
- **Voting Mechanism:** Users vote on posts based on a combination of their adjusted goodness (affected by mood) and the quality of the post.
- **Multi-Stage Voting:**
  - For populations with fewer than 20 high-ELO users, a single stage of voting is performed.
  - For larger populations, a two-stage process is used:
    - **Stage 1:** A sample from the lower ELO tier (bottom 70%) votes. The sample size scales with population size.
    - **Stage 2:** If the first stage decision is inconclusive, a sample from the upper ELO tier (top 30%) is used to validate the decision.
  - **Special Stage:** Low-ELO users (≤ 800) vote separately, and their votes are used only to adjust their own ELO scores.
- **Population Sample Voting:** An alternative voting mechanism that uses statistically significant samples from the entire population to make decisions.
- **ELO Adjustments:** User ratings are updated based on vote outcomes using team-based ELO updates.
- **Visualization:** After simulation runs, various plots display:
  - Distribution of user goodness and ELO ratings
  - Comparison of correct votes ratio between staged and population sample voting
  - Population growth over time
  - Sample sizes used in voting
  - Voting participation ratios by user group
  - Linear regression analysis of voting accuracy trends

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

   - Grow the user population gradually until it reaches 5,000 users.
   - Generate posts (approximately 2 per user) and simulate both multi-stage and population sample voting processes.
   - Update users' ELO ratings based on voting accuracy.
   - Display comprehensive visualizations comparing different voting mechanisms and their effectiveness.

## Relationship to the Whitepaper

This simulation serves as a practical implementation of the theoretical framework described in the [Veridonia Whitepaper](Whitepaper.md). While the whitepaper provides the complete conceptual principles and governance model, this simulation focuses specifically on testing the effectiveness of the multi-stage voting and ELO-based reputation mechanisms.

The whitepaper covers additional topics not implemented in this simulation, including:

- Detailed discussion of problems with current content curation systems
- More comprehensive governance frameworks
- Data privacy considerations
- Long-term vision for transparent information ecosystems

For a deeper understanding of the Veridonia concept, please refer to the whitepaper.

## Acknowledgements

This simulation is a proof-of-concept implementation based on the principles outlined in the Veridonia whitepaper. It aims to explore the potential of community-driven content curation and transparent reputation systems.

---

Feel free to contribute, report issues, or suggest improvements by opening an issue or pull request in the repository.

Happy simulating!
