import random
import numpy as np
import matplotlib.pyplot as plt
from termcolor import colored
from tqdm import tqdm
import math
import scipy.stats as st


class User:
    def __init__(self, id, elo=800):
        self.id = id
        self.elo = elo
        self.goodness = self.generate_goodness()
        self.mood_factor = random.uniform(0, 0.1)  # Random value from 0 to 0.1
        self.adjusted_goodness = self.goodness
        self.vote_count = 0

    def generate_goodness(self):
        goodness = np.random.exponential(scale=0.3)  # Adjusted scale to 0.3
        if goodness > 1:
            goodness = np.random.uniform()
        return goodness

    def apply_mood(self):
        self.adjusted_goodness = self.goodness
        if random.random() < self.mood_factor:
            adjustment = random.uniform(0, 0.25)
            if random.choice([True, False]):
                self.adjusted_goodness = min(1, self.goodness * (1 + adjustment))
            else:
                self.adjusted_goodness = max(0, self.goodness * (1 - adjustment))


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
    user.vote_count += 1
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
            user.elo += change_per_loser  # (it's negative, so they lose Elo)
    return votes, stage_decision


def elo_update_team(winner_avg_elo, loser_avg_elo, k=32, winner_size=1, loser_size=1):
    expected_score_winner = 1 / (1 + 10 ** ((loser_avg_elo - winner_avg_elo) / 400))
    expected_score_loser = 1 - expected_score_winner
    total_winner_delta = k * (1 - expected_score_winner)
    total_loser_delta = k * (0 - expected_score_loser)
    change_per_winner = total_winner_delta / winner_size
    change_per_loser = total_loser_delta / loser_size
    return change_per_winner, change_per_loser


def multi_stage_voting(post, all_users):
    """
    Implements a two-stage voting mechanism for a given post using ELO tiers.
    Only considers users with elo > 800.
    If the number of filtered users is less than 20, a single stage voting is performed by selecting 5 users from the filtered users.
    Otherwise:
      - Stage 1: Bottom 70% of the filtered users (select 5 users)
      - Stage 2: Top 30% of the filtered users (select 5 users)
    After the final decision is determined, a special stage is executed for users with elo <= 800.
    This special stage selects 5 users from the low-elo group and adjusts their elo based on whether their vote matches the final decision.
    Their votes do not affect the overall decision or metrics.
    """
    # Filter users with elo > 800
    filtered_users = [user for user in all_users if user.elo > 800]
    if not filtered_users:
        filtered_users = all_users

    if not filtered_users:
        return [], "downvote", 0

    sorted_users = sorted(filtered_users, key=lambda u: u.elo)
    N = len(sorted_users)
    sample_size = 0

    # If there are less than 20 filtered users, perform single stage voting
    if N < 20:
        stage_users = sorted_users if N <= 5 else random.sample(sorted_users, 5)
        votes, decision = stage_voting(stage_users, post, forfeit_bonus=0)
        sample_size += len(votes)
    else:
        # Otherwise, perform two-stage voting
        # Stage 1: Bottom 70% of the filtered users
        stage1_group = sorted_users[: int(0.7 * N)]
        stage1_users = (
            stage1_group if len(stage1_group) <= 5 else random.sample(stage1_group, 5)
        )
        votes1, decision1 = stage_voting(stage1_users, post, forfeit_bonus=0)
        sample_size += len(votes1)
        if decision1 != "upvote":
            votes, decision = votes1, decision1
        else:
            # Stage 2: Top 30% of the filtered users
            stage2_group = sorted_users[int(0.7 * N) :]
            stage2_users = (
                stage2_group
                if len(stage2_group) <= 5
                else random.sample(stage2_group, 5)
            )
            votes2, decision2 = stage_voting(stage2_users, post, forfeit_bonus=0)
            sample_size += len(votes2)
            votes, decision = votes2, decision2

    # Special stage for users with elo <= 800 (only if final decision is 'upvote' or 'downvote')
    if decision in ["upvote", "downvote"]:
        low_elo_users = [user for user in all_users if user.elo <= 800]
        if low_elo_users:
            special_users = (
                low_elo_users
                if len(low_elo_users) <= 5
                else random.sample(low_elo_users, 5)
            )
            special_votes = []
            for user in special_users:
                # Get the user's vote without affecting overall metrics
                vote_decision = vote(user, post)
                special_votes.append((user, vote_decision))
            winners = [user for user, v in special_votes if v == decision]
            losers = [user for user, v in special_votes if v != decision]
            if winners and losers:
                average_winner_elo = sum(u.elo for u in winners) / len(winners)
                average_loser_elo = sum(u.elo for u in losers) / len(losers)
                change_per_winner, change_per_loser = elo_update_team(
                    average_winner_elo,
                    average_loser_elo,
                    k=32,
                    winner_size=len(winners),
                    loser_size=len(losers),
                )
                for user in winners:
                    user.elo += change_per_winner
                for user in losers:
                    user.elo += change_per_loser

    return votes, decision, sample_size


def run_simulation():
    posts_per_user = 2  # Approximate a more realistic tweet-like frequency
    max_population = 10000

    with tqdm(total=max_population, desc="Growing user population") as pbar:
        posts = []
        upvoted_posts_quality = []
        upvoted_posts_count = 0
        total_votes = 0
        correct_votes = 0
        correct_votes_stats = []
        votes_stats = []
        population_sizes = []
        sample_sizes = []
        cumulative_votes_list = []
        users = []

        growth_rate = 0.10
        population_increment = 1.0  # Start by adding 1 user at a time
        while len(users) < max_population:
            new_count = min(
                math.ceil(population_increment), max_population - len(users)
            )
            new_users = [User(i) for i in range(len(users), len(users) + new_count)]
            users.extend(new_users)

            new_posts = [
                Post(i)
                for i in range(len(posts), len(posts) + (posts_per_user * new_count))
            ]
            posts.extend(new_posts)

            for post in new_posts:
                votes, decision, post_sample_size = multi_stage_voting(post, users)
                total_votes += 1  # Count one final decision per post

                if (decision == "upvote" and post.quality >= 0.5) or (
                    decision == "downvote" and post.quality < 0.5
                ):
                    correct_votes += 1
                    correct_votes_stats.append(1)
                else:
                    correct_votes_stats.append(0)

                votes_stats.append((post.id, decision))
                if decision == "upvote":
                    upvoted_posts_count += 1
                    upvoted_posts_quality.append(post.quality)

                cumulative_votes_list.append(total_votes)
                sample_sizes.append(post_sample_size)

            # Append the population size once per iteration
            population_sizes.append(len(users))
            pbar.update(new_count)
            pbar.set_postfix(current=len(users))
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
        sample_sizes,
        cumulative_votes_list,
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
    stage_result_colored = colored(
        stage_result, color_mapping.get(stage_result, "default_color")
    )
    print(f"Stage {stage} majority decision: {stage_result_colored}\n")


def aggregate_votes(votes, chunk_size):
    aggregated_data = []
    for i in range(0, len(votes), chunk_size):
        chunk = votes[i : i + chunk_size]
        proportion_correct = np.sum(chunk) / len(chunk) * 100
        aggregated_data.append(proportion_correct)
    return aggregated_data


def plot_distributions(
    users,
    upvoted_posts_quality,
    correct_votes_stats,
    population_sizes,
    sample_sizes,
    cumulative_votes_list,
):
    plt.figure(figsize=(12, 7))

    # Subplot 1: Distribution of Users by Goodness Factor
    plt.subplot(2, 3, 1)
    plt.hist([user.goodness for user in users], bins=100, edgecolor="black")
    plt.xlabel("Goodness Factor")
    plt.ylabel("Number of Users")
    plt.title("Distribution of Users by Goodness Factor")

    # Subplot 2: Distribution of Users by Elo Rating
    plt.subplot(2, 3, 2)
    plt.hist([user.elo for user in users], bins=100, edgecolor="black", log=True)
    plt.xlabel("Elo Rating")
    plt.ylabel("Number of Users")
    plt.title("Distribution of Users by Elo Rating")

    # Subplot 3: Proportion of Correct Votes Over Time
    plt.subplot(2, 3, 3)
    if len(correct_votes_stats) > 10:
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
    plt.xlabel("Stage Index")
    plt.ylabel("Proportion of Correct Votes (%)")
    plt.ylim(0, 100)
    plt.grid(True)

    # Subplot 4: Population Over Time
    plt.subplot(2, 3, 4)
    plt.plot(range(len(population_sizes)), population_sizes, label="Population Size")
    plt.xlabel("Stage Index")
    plt.ylabel("Population Size")
    plt.title("Population Over Time")

    # Subplot 5: Max Vote Ratio Over Time
    plt.subplot(2, 3, 5)
    max_vote_ratio = [
        (
            (sample_sizes[i] / cumulative_votes_list[i]) * 100
            if cumulative_votes_list[i] > 0
            else 0
        )
        for i in range(len(sample_sizes))
    ]
    plt.plot(range(len(max_vote_ratio)), max_vote_ratio, color="r")
    plt.xlabel("Stage Index")
    plt.ylabel("Max Vote Ratio (%)")
    plt.title("Max Vote Ratio Over Time")

    # Subplot 6: Sample Size Used Over Time
    plt.subplot(2, 3, 6)
    plt.plot(range(len(sample_sizes)), sample_sizes, color="g")
    plt.xlabel("Stage Index")
    plt.ylabel("Number of Voters")
    plt.title("Sample Size Used Over Time")

    plt.tight_layout()
    plt.show()


users = run_simulation()
