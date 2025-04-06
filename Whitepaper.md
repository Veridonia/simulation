# Veridonia

## A Whitepaper on Transparent, Community-Driven Information Curation

### Abstract

Veridonia introduces a transformative approach to online content curation, addressing the limitations of conventional, engagement-driven systems that have fuelled sensationalism, misinformation, and the creation of echo chambers. ([1](https://doi.org/10.1016/j.tics.2021.02.007), [2](https://doi.org/10.1126/science.aao2998), [3](https://doi.org/10.1073/pnas.2023301118)) This whitepaper outlines the challenges posed by today's digital information ecosystem and details the design, architecture, and operational principles of Veridonia. Central to our approach is a multi-stage voting mechanism coupled with an ELO-based reputation system, which together foster transparency, meritocracy, and community governance. Veridonia's framework ensures that only high-quality, rigorously vetted information reaches the public domain whilst safeguarding user privacy and resisting external manipulation.

### 1. Introduction

The digital landscape today is dominated by engagement metrics such as views, likes, and shares, which serve as the primary indicators of content performance. This focus on the attention economy has led to the widespread prioritisation of sensationalist content over substantive information, contributing to the rapid spread of misinformation, the formation of ideological echo chambers, and a general decline in content quality. ([1](https://doi.org/10.1016/j.tics.2021.02.007), [2](https://doi.org/10.1126/science.aao2998), [3](https://doi.org/10.1073/pnas.2023301118)) Furthermore, opaque algorithms that dictate content visibility and maximise engagement at any cost have amplified mistrust and decreased accountability ([4](https://doi.org/10.1177/1461444816676645)).

The current paradigm of social media platforms is fundamentally misaligned with the broader interests of society. Rather than facilitating meaningful information exchange, these systems have evolved into attention-capture mechanisms engineered to maximise screen time. Their algorithms prioritise engagement through psychological manipulation, often at the expense of informative or socially valuable content. As a result, content with the highest emotional appeal—not necessarily the highest quality—achieves the greatest visibility, while important discourse is frequently relegated to the margins.

Veridonia is conceived as a response to these challenges. By re-engineering the content curation process, Veridonia aims to restore public trust in online content and empower communities to determine quality based on transparent, verifiable standards rather than commercial or algorithmic bias.

### 2. Problem Statement

The prevailing model for information sharing suffers from several critical flaws:

1. **Sensationalist Content Over Substantive Information:** Content is often designed to attract clicks and emotional responses rather than provide well-researched, balanced perspectives ([2](https://doi.org/10.1126/science.aao2998)).
2. **Misinformation Propagation:** The race for engagement results in the rapid spread of false or misleading information ([1](https://doi.org/10.1016/j.tics.2021.02.007)).
3. **Filter Bubbles and Echo Chambers:** Personalised algorithms confine users to ideologically homogenous groups, diminishing exposure to diverse viewpoints ([2](https://doi.org/10.1126/science.aao2998)).
4. **Opaque Decision-Making:** Hidden algorithmic processes limit transparency and accountability, fostering widespread mistrust ([4](https://doi.org/10.1177/1461444816676645)).
5. **Negative Societal Impacts:** The relentless pursuit of engagement contributes significantly to mental health issues and decreased productivity ([5](https://doi.org/10.1080/02673843.2019.1590851)).

### 3. Veridonia's Proposed Solution

Veridonia replaces the opaque, engagement-centric model with a transparent, community-powered framework. Our system leverages a multi-stage voting process and an ELO-based reputation mechanism to ensure that content quality is determined by merit and consensus. Key aspects of our approach include:

- **Community-Driven Moderation:** Every piece of content is rigorously vetted by a cross-section of the user base.
- **Transparent Algorithms:** All decisions, votes, and reputation adjustments are publicly recorded, allowing for independent verification.
- **Self-Governance:** Veridonia is fundamentally governed by its community, empowering every member to contribute to decision-making. The platform operates without centralised authority, ensuring that content curation remains decentralised and inclusive. The only exception is when community actions, such as posting outright illegal content, threaten the platform's very existence.
- **Resistance to Manipulation:** Randomised participant selection minimises the risk of coordinated attacks or manipulation by malicious entities.

### 4. System Architecture

**4.1 User Onboarding and Baseline Attributes**

- **Initial Equality:** Upon joining, every user (registered or guest) is assigned a baseline ELO rating (e.g., 800), ensuring equal initial influence.
- **Reputation Development:** Users' influence in content curation evolves over time, reflecting the accuracy and consistency of their judgements.

**4.2 Post Submission**

When a post is submitted, a random subset of relevant community members is selected to review the content. This randomness is essential to ensure that decisions reflect genuine community consensus rather than the influence of targeted manipulation.

### 5. Multi-Stage Voting Process

Veridonia employs a dynamic, two-stage voting mechanism designed for accuracy, transparency, and scalability. The system operates similarly to a series of community referendums, where a small, carefully selected group of voters represents the broader community's likely preferences. This approach allows us to efficiently determine whether content should be published without requiring every community member to vote on every piece of content, whilst maintaining the integrity and accuracy of the decision-making process.

**5.1 Stage 1: Initial Filtering**

- Participants: A random sample selected from users in the lower 70% ELO tier (above a minimum ELO threshold, typically ELO > 800).
- Decision Criterion: Participants assess content quality and community alignment.
- Outcome:
  - If at least 70% consensus is achieved (either approval or rejection), the decision is immediately finalised.
  - If consensus falls below 70%, the voting advances to Stage 2 for a final decision.

**5.2 Stage 2: Final Decision (Conditional)**

- Participants: A random sample from the top 30% ELO tier of eligible voters.
- Decision Criterion: A simple majority finalises the content decision.
- Outcome: The content is either approved ("publish") or rejected ("delete") based on the majority decision.

**Special Conditions:**

- For populations with fewer than 20 eligible voters, a simplified single-stage voting process is employed.
- After the primary voting stages, a special, non-decisional voting stage occurs involving a small subset (up to 5) of low-ELO users (ELO ≤ 800). This stage does not influence the content approval decision and is solely for giving a second chance to the users who have previously misbehaved and to test the users who have just joined the community.

### 6. ELO-Based Reputation System

The ELO-based reputation system is central to Veridonia's meritocratic model:

- **Dynamic Influence:** Users' ELO ratings not only reflect their decision-making accuracy but also serve as a gateway to enhanced moderation privileges. As users consistently align with community standards and see their ratings increase, they become eligible for promotion from the initial tier to higher groups—Stage 2 or Stage 3 group. These promotions grant them greater influence over content curation and the overall quality of the platform.
- **Zero-Sum ELO Adjustments:** Post-evaluation, votes are compared against the post's assessed quality. Points are reallocated—users in the majority gain influence, whilst those in the minority see a corresponding decrease.
- **Team-Based Reputation Adjustments:** When users vote on a piece of content, they form two groups: those whose votes match the final outcome ("winners") and those whose votes oppose it ("losers"). To adjust reputation ratings (ELO):

  1. The average ELO rating for each group (winners and losers) is calculated separately.
  2. Each user's new ELO is updated based on how their group's average compares to the opposing group's average, scaled by a predefined constant (K-factor).
  3. Winners gain ELO, moving their ratings upward towards the opposing group's average rating, whilst losers lose ELO, moving downward towards the winners' average.
  4. This method promotes accuracy and fairness by rewarding collective correct judgements and gradually increasing the decision-making influence of consistently accurate users.

### 7. Transparency and Self-Governance

Veridonia is designed to be an open and self-regulating ecosystem:

- **Public Auditability:** All voting records, ELO adjustments, and moderation actions are logged and accessible for independent review, emulating blockchain-like transparency.
- **Decentralised Moderation:** Governance is vested in the community, with every member (including guests) empowered to contribute, vote, and shape content standards.
- **Data Privacy:** Whilst maintaining openness, Veridonia is committed to robust data privacy practices, allowing users to download and verify all activity history without compromising security.

### 8. Additional Core Principles

- **Independence from Advertiser Influence:** Veridonia is free from advertiser funding, ensuring that content curation remains unbiased and dictated solely by community standards.
- **Integrity in Information Sharing:** By prioritising transparency and quality, Veridonia mitigates the risks of misinformation and preserves the integrity of the information ecosystem.
- **User Empowerment:** The platform is structured to empower users, granting them direct oversight of the content curation process without the interference of centralised authorities.

### 9. Conclusion

Veridonia represents a bold new vision for online information sharing—a system that replaces opaque, engagement-driven algorithms with a transparent, community-powered model. Through its innovative multi-stage voting process and dynamic ELO-based reputation system, Veridonia ensures that only content meeting quality standards is published. In doing so, it addresses the deep-seated issues of misinformation, sensationalism, and algorithmic opacity prevalent in today's digital media landscape.

By restoring trust and empowering communities to govern their own content, Veridonia lays the groundwork for a more balanced and informed digital ecosystem. In an era where information is too often manipulated for profit and power, Veridonia stands as a beacon of integrity and transparency.

### References

1. Pennycook, G., & Rand, D. G. (2021). "The Psychology of Fake News." _Trends in Cognitive Sciences_, 25(5), 388–402. [https://doi.org/10.1016/j.tics.2021.02.007](https://doi.org/10.1016/j.tics.2021.02.007)

2. Lazer, D. M. J., Baum, M. A., Benkler, Y., Berinsky, A. J., Greenhill, K. M., Menczer, F., & Zittrain, J. L. (2018). "The Science of Fake News." _Science_, 359(6380), 1094–1096. [https://doi.org/10.1126/science.aao2998](https://doi.org/10.1126/science.aao2998)

3. Cinelli, M., Morales, G. D. F., Galeazzi, A., Quattrociocchi, W., & Starnini, M. (2021). "The Echo Chamber Effect on Social Media." _Proceedings of the National Academy of Sciences_, 118(9). [https://doi.org/10.1073/pnas.2023301118](https://doi.org/10.1073/pnas.2023301118)

4. Ananny, M., & Crawford, K. (2018). "Seeing without Knowing: Limitations of the Transparency Ideal and Its Application to Algorithmic Accountability." _New Media & Society_, 20(3), 973–989. [https://doi.org/10.1177/1461444816676645](https://doi.org/10.1177/1461444816676645)

5. Keles, B., McCrae, N., & Grealish, A. (2020). "A Systematic Review: The Influence of Social Media on Depression, Anxiety, and Psychological Distress in Adolescents." _International Journal of Adolescence and Youth_, 25(1), 79–93. [https://doi.org/10.1080/02673843.2019.1590851](https://doi.org/10.1080/02673843.2019.1590851)
