import random
import numpy as np
import matplotlib.pyplot as plt
from termcolor import colored
from tqdm import tqdm
import math
import scipy.stats as st

z = 1.645  # Z-score for 90% confidence
p = 0.5  # assumed proportion
E = 0.05  # margin of error (5%)
sample_size = math.ceil((z**2 * p * (1 - p)) / (E**2))


class User:
    def __init__(self, id, elo=800):
        self.id = id
        self.elo = elo
        self.goodness = self.generate_goodness()
        self.mood_factor = random.uniform(0, 0.1)  # Random value from 0 to 0.1
        self.adjusted_goodness = self.goodness
        self.vote_count = 0

    def generate_goodness(self):
        goodness = np.random.exponential(scale=0.1)  # Adjusted scale to 0.3
        if goodness > 1:
            goodness = np.random.uniform()
        return goodness

    def apply_mood(self):
        self.adjusted_goodness = self.goodness
        if random.random() < self.mood_factor:
            adjustment = random.uniform(0, 0.25)
            if random.choice([True, False]):
                self.adjusted_goodness = min(
                    1, self.goodness * (1 + adjustment)
                )  # Increase goodness by 0% to 25%
            else:
                self.adjusted_goodness = max(
                    0, self.goodness * (1 - adjustment)
                )  # Decrease goodness by 0% to 25%


class Post:
    def __init__(self, id):
        self.id = id
        self.quality = random.uniform(0, 1)


def elo_update(winner_elo, loser_elo, k=32):
    expected_score = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    new_winner_elo = winner_elo + k * (1 - expected_score)
    new_loser_elo = loser_elo - k * (1 - expected_score)
    return new_winner_elo, new_loser_elo


def vote(user, post):
    user.apply_mood()  # Update adjusted goodness before voting
    if post.quality >= 0.5:
        vote_decision = (
            "upvote"
            if random.uniform(0, 1) < user.adjusted_goodness
            else random.choice(["downvote", "upvote"])
        )
    else:
        vote_decision = (
            "downvote"
            if random.uniform(0, 1) < user.adjusted_goodness
            else random.choice(["downvote", "upvote"])
        )
    return vote_decision


def stage_voting(stage_users, post, forfeit_bonus=0):
    votes = []
    stage_decision = "draw"
    for user in stage_users:
        vote_decision = vote(user, post)
        votes.append((user, vote_decision))

    upvotes = [user for user, vote in votes if vote == "upvote"]
    downvotes = [user for user, vote in votes if vote == "downvote"]

    if not upvotes and downvotes:
        winning_team = downvotes
        losing_team = upvotes
        stage_decision = "downvote"
    elif not downvotes and upvotes:
        winning_team = upvotes
        losing_team = downvotes
        stage_decision = "upvote"
    elif len(upvotes) > len(downvotes):
        winning_team = upvotes
        losing_team = downvotes
        stage_decision = "upvote"
    elif len(downvotes) > len(upvotes):
        winning_team = downvotes
        losing_team = upvotes
        stage_decision = "downvote"
    else:
        return votes, stage_decision

    if not losing_team:
        if len(votes) > 1:
            # Forfeit case: Winning team gets a small fixed number of points
            for user in winning_team:
                user.elo += forfeit_bonus
    else:
        average_winner_elo = sum(user.elo for user in winning_team) / len(winning_team)
        average_loser_elo = sum(user.elo for user in losing_team) / len(losing_team)

        change_per_winner, change_per_loser = elo_update_team(
            average_winner_elo,
            average_loser_elo,
            k=32,
            winner_size=len(winning_team),
            loser_size=len(losing_team),
        )

        for user in winning_team:
            user.elo += change_per_winner
        for user in losing_team:
            user.elo += change_per_loser  # (it’s negative, so they lose Elo)

    return votes, stage_decision


def elo_update_team(winner_avg_elo, loser_avg_elo, k=32, winner_size=1, loser_size=1):
    # 1. Compute the winner's expected score in a 2-team match
    expected_score_winner = 1 / (1 + 10 ** ((loser_avg_elo - winner_avg_elo) / 400))

    # 2. The losers' expected score is the complement
    expected_score_loser = 1 - expected_score_winner

    # 3. Compute total rating change for each side (team-level)
    total_winner_delta = k * (1 - expected_score_winner)  # winners' actual score = 1
    total_loser_delta = k * (0 - expected_score_loser)  # losers' actual score = 0

    # 4. Divide equally among individuals in each team
    change_per_winner = total_winner_delta / winner_size
    change_per_loser = total_loser_delta / loser_size
    return change_per_winner, change_per_loser


def run_simulation():
    posts_per_user = 2  # Approximate a more realistic tweet‐like frequency
    max_population = 10000

    with tqdm(total=max_population, desc="Growing user population") as pbar:
        population = 1
        posts = []
        upvoted_posts_quality = []
        upvoted_posts_count = 0
        total_votes = 0
        correct_votes = 0
        correct_votes_stats = []
        votes_stats = []
        population_sizes = []
        max_vote_counts = []
        cumulative_votes_list = []
        sample_used_list = []
        users = []
        confidence_levels = []

        growth_rate = 0.10
        population_increment = 1.0  # Start by adding 1 user at a time
        while len(users) < max_population:
            # Determine how many new users to add, but do not exceed max_population
            new_count = min(
                math.ceil(population_increment), max_population - len(users)
            )
            new_users = [User(i) for i in range(len(users), len(users) + new_count)]
            users.extend(new_users)

            # Use the current population size (N) for the finite population correction formula
            N = len(users)
            sample_size_fp = math.ceil(
                (N * (z**2 * p * (1 - p))) / ((E**2 * (N - 1)) + (z**2 * p * (1 - p)))
            )
            sample_size = sample_size_fp

            # Calculate effective confidence level using the finite population correction
            if sample_size >= N:
                effective_confidence = (
                    1.0  # Full confidence if the entire population is sampled
                )
            else:
                # Invert the finite population correction: sample_size = n0 * N / (n0 + N - 1) => n0 = (sample_size * (N - 1)) / (N - sample_size)
                effective_n0 = (sample_size * (N - 1)) / (N - sample_size)
                # Compute effective Z-score from n0: n0 = (z^2 * p * (1 - p)) / (E**2) => z_eff = sqrt(n0 * (E**2) / (p * (1 - p)))
                z_eff = math.sqrt(effective_n0 * (E**2) / (p * (1 - p)))
                effective_confidence = 2 * st.norm.cdf(z_eff) - 1

            confidence_levels.append(effective_confidence)

            # Generate posts for these new users
            new_posts = [
                Post(i)
                for i in range(len(posts), len(posts) + (posts_per_user * new_count))
            ]
            posts.extend(new_posts)

            # Vote on these new posts
            for post in new_posts:
                if len(users) < sample_size:
                    selected_users = users
                else:
                    selected_users = random.sample(users, sample_size)

                for user in selected_users:
                    user.vote_count += 1

                votes, decision = stage_voting(selected_users, post, forfeit_bonus=0)
                total_votes += 1

                if (decision == "upvote" and post.quality >= 0.5) or (
                    decision == "downvote" and post.quality < 0.5
                ):
                    correct_votes += 1
                    correct_votes_stats.append(1)
                else:
                    correct_votes_stats.append(0)
                votes_stats.append(
                    (1, post, votes, decision, users, sample_size, sample_size)
                )
                if decision == "upvote":
                    upvoted_posts_count += 1
                    upvoted_posts_quality.append(post.quality)

            # Record stage statistics
            max_vote_counts.append(max(user.vote_count for user in users))
            cumulative_votes_list.append(total_votes)
            sample_used_list.append(min(len(users), sample_size))
            population_sizes.append(len(users))

            # Update the tqdm progress bar using the number of new users added
            pbar.update(new_count)
            pbar.set_postfix(current=len(users))

            # Increase the user addition increment for the next stage
            population_increment *= 1 + growth_rate

    print(f"Number of posts upvoted through all voting: {upvoted_posts_count}")
    print(f"Number of correct votes: {correct_votes}")
    print(f"Total number of votes: {total_votes}")
    print(f"Correct votes: {(correct_votes / total_votes) * 100:.2f}%")

    plot_distributions(
        users,
        upvoted_posts_quality,
        correct_votes_stats,
        population_sizes,
        max_vote_counts,
        cumulative_votes_list,
        sample_used_list,
        confidence_levels,
    )
    return users


def printStageResult(
    stage, post, votes, stage_result, users, users_stage_count, num_stage_users
):
    print(f"Stage {stage} voting for Post {post.id} (Quality: {post.quality:.2f}):")
    print(
        f"Total users: {len(users)}; In stage: {users_stage_count}; Selected: {num_stage_users}"
    )
    for user, vote in votes:
        color_mapping = {"upvote": "green", "downvote": "red", "draw": "yellow"}

        vote_colored = colored(vote, color_mapping.get(vote, "default_color"))
        print(
            f"User {user.id} (Adj. Goodness: {user.adjusted_goodness:.2f}, ELO: {user.elo:.2f}) voted {vote_colored}"
        )
    stage1_result_colored = colored(
        stage_result, color_mapping.get(stage_result, "default_color")
    )
    print(f"Stage {stage} majority decision: {stage1_result_colored}\n")


# Function to aggregate values by chunks of n and calculate proportion of correct votes
def aggregate_votes(votes, chunk_size):
    aggregated_data = []
    for i in range(0, len(votes), chunk_size):
        chunk = votes[i : i + chunk_size]
        proportion_correct = np.sum(chunk) / len(chunk) * 100  # Convert to percentage
        aggregated_data.append(proportion_correct)
    return aggregated_data


def plot_distributions(
    users,
    upvoted_posts_quality,
    correct_votes_stats,
    population_sizes,
    max_vote_counts,
    cumulative_votes_list,
    sample_used_list,
    confidence_levels,
):
    # Arrange plots in a grid with 3 rows and 3 columns to accommodate 7 subplots
    plt.figure(figsize=(10, 8))

    # Subplot 1: Distribution of Users by Goodness Factor
    plt.subplot(3, 3, 1)
    plt.hist([user.goodness for user in users], bins=100, edgecolor="black")
    plt.xlabel("Goodness Factor")
    plt.ylabel("Number of Users")
    plt.title("Distribution of Users by Goodness Factor")

    # Subplot 2: Distribution of Users by Elo Rating
    plt.subplot(3, 3, 2)
    plt.hist([user.elo for user in users], bins=100, edgecolor="black", log=True)
    plt.xlabel("Elo Rating")
    plt.ylabel("Number of Users")
    plt.title("Distribution of Users by Elo Rating")

    # Subplot 3: Proportion of Correct Votes Over Time
    plt.subplot(3, 3, 3)
    # Use a moving average to smooth the proportion of correct votes
    if len(correct_votes_stats) > 10:
        # For small datasets use a smaller window; for larger ones, scale the window size
        if len(correct_votes_stats) < 50:
            window_size = min(10, len(correct_votes_stats))
        else:
            window_size = max(10, int(len(correct_votes_stats) / 100))
        smoothed = (
            np.convolve(
                correct_votes_stats, np.ones(window_size) / window_size, mode="valid"
            )
            * 100
        )
        plt.plot(range(len(smoothed)), smoothed, linestyle="-", color="b")
    else:
        plt.plot(
            range(len(correct_votes_stats)),
            np.array(correct_votes_stats) * 100,
            linestyle="-",
            color="b",
        )
    plt.title("Proportion of Correct Votes Over Time")
    plt.xlabel(f"Stage Index")
    plt.ylabel("Proportion of Correct Votes (%)")
    plt.ylim(0, 100)
    plt.grid(True)

    # Subplot 4: Population Over Time
    plt.subplot(3, 3, 4)
    plt.plot(
        range(len(population_sizes)),
        population_sizes,
        label="Population Size",
    )
    plt.xlabel("Stage Index")
    plt.ylabel("Population Size")
    plt.title("Population Over Time")

    # Subplot 5: Max Vote Ratio Over Time
    plt.subplot(3, 3, 5)
    # Calculate max vote ratio as the maximum vote count divided by the cumulative votes at that stage
    max_vote_ratio = [
        (
            (max_vote_counts[i] / cumulative_votes_list[i]) * 100
            if cumulative_votes_list[i] > 0
            else 0
        )
        for i in range(len(max_vote_counts))
    ]
    plt.plot(
        range(len(max_vote_ratio)),
        max_vote_ratio,
        color="r",
    )
    plt.xlabel("Stage Index")
    plt.ylabel("Max Vote Ratio (%)")
    plt.title("Max Vote Ratio Over Time")

    # Subplot 6: Sample Size Used Over Time
    plt.subplot(3, 3, 6)
    plt.plot(
        range(len(sample_used_list)),
        sample_used_list,
        color="g",
    )
    plt.xlabel("Stage Index")
    plt.ylabel("Number of Voters")
    plt.title("Sample Size Used Over Time")

    # Subplot 7: Confidence Level Over Time
    plt.subplot(3, 3, 7)
    plt.plot(
        range(len(confidence_levels)),
        [c * 100 for c in confidence_levels],
        color="m",
        linestyle="-",
    )
    plt.xlabel("Stage Index")
    plt.ylabel("Confidence Level (%)")
    plt.title("Confidence Level Over Time")
    plt.ylim(0, 100)
    plt.grid(True)

    plt.tight_layout()
    plt.show()


# Run simulation
users = run_simulation()
