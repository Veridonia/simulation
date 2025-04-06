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


def calculate_sample_size(confidence, margin_of_error, population_size):
    """
    Calculate sample size needed for given confidence level and margin of error.

    Args:
        confidence: Confidence level (e.g., 0.95 for 95%)
        margin_of_error: Margin of error (e.g., 0.05 for 5%)
        population_size: Size of the population to sample from

    Returns:
        Required sample size
    """
    # Z score for given confidence level
    z = st.norm.ppf(1 - (1 - confidence) / 2)

    # Use 0.5 for p (worst case scenario for sample size)
    p = 0.5

    # Sample size calculation
    numerator = (z**2 * p * (1 - p)) / (margin_of_error**2)
    denominator = 1 + (z**2 * p * (1 - p)) / (margin_of_error**2 * population_size)

    sample_size = numerator / denominator
    return math.ceil(sample_size)


def population_sample_voting(
    post, current_population, confidence=0.95, margin_of_error=0.05
):
    """
    Voting stage where a statistically significant sample of the current population votes,
    using a sample size calculated to achieve the desired confidence level and error margin.

    This voting does not influence Elo adjustments.

    Args:
        post: The post to vote on
        current_population: Current population of users
        confidence: Confidence level (default: 0.95)
        margin_of_error: Margin of error (default: 0.05)

    Returns:
        tuple: (votes, decision, sample_size)
    """
    if not current_population:
        return [], "downvote", 0

    # Calculate required sample size
    population_size = len(current_population)
    required_sample_size = calculate_sample_size(
        confidence, margin_of_error, population_size
    )

    # Ensure we don't try to sample more users than available
    sample_size = min(required_sample_size, population_size)

    # Select random users from all users
    sample_users = (
        current_population
        if sample_size >= population_size
        else random.sample(current_population, sample_size)
    )

    # Get votes without affecting Elo
    votes = []
    for user in sample_users:
        vote_decision = vote(user, post)
        votes.append((user, vote_decision))

    # Determine decision
    upvotes = [user for user, vote in votes if vote == "upvote"]
    downvotes = [user for user, vote in votes if vote == "downvote"]

    if not upvotes and downvotes:
        decision = "downvote"
    elif not downvotes and upvotes:
        decision = "upvote"
    elif len(upvotes) > len(downvotes):
        decision = "upvote"
    elif len(downvotes) > len(upvotes):
        decision = "downvote"
    else:
        decision = "draw"

    return votes, decision, sample_size


def multi_stage_voting(post, all_users):
    """
    Implements a two-stage voting mechanism for a given post using ELO tiers.
    Only considers users with elo > 800.
    If the number of filtered users is less than 20, a single stage voting is performed by selecting 5 users from the filtered users.
    Otherwise:
      - Stage 1: Bottom 70% of the filtered users (select users based on population size)
      - Stage 2: Top 30% of the filtered users (select 5 users) - only if Stage 1 was inconclusive
    A decision is considered conclusive if 70% or more of the voters agree.
    After the final decision is determined, a special stage is executed for users with elo <= 800.
    This special stage selects 5 users from the low-elo group and adjusts their elo based on whether their vote matches the final decision.
    Their votes do not affect the overall decision or metrics.
    """

    # Calculate the number of stage 1 users based on population size
    def get_stage1_user_count(population_size):
        if population_size < 1000:
            return 5  # Default for small populations
        else:
            # For every 1000 users, add 1 to the count, up to a maximum of 10
            additional_users = min((population_size - 1000) // 1000, 5)
            return 5 + additional_users

    # Filter users with elo > 800
    filtered_users = [user for user in all_users if user.elo > 800]
    if not filtered_users:
        filtered_users = all_users

    if not filtered_users:
        return (
            [],
            "downvote",
            0,
            [],
            [],
            [],
        )  # Added empty lists for stage1, stage2, low_elo participants

    sorted_users = sorted(filtered_users, key=lambda u: u.elo)
    N = len(sorted_users)
    sample_size = 0

    # Get the number of stage 1 users based on the total population
    stage1_user_count = get_stage1_user_count(len(all_users))

    # Lists to track which users participated in each stage
    stage1_participants = []
    stage2_participants = []
    low_elo_participants = []

    # If there are less than 20 filtered users, perform single stage voting
    if N < 20:
        stage_users = (
            sorted_users
            if N <= stage1_user_count
            else random.sample(sorted_users, stage1_user_count)
        )
        votes, decision = stage_voting(stage_users, post, forfeit_bonus=0)
        sample_size += len(votes)
        stage1_participants = [
            user for user, _ in votes
        ]  # Consider these as stage 1 participants
    else:
        # Stage 1: Bottom 70% of the filtered users
        stage1_group = sorted_users[: int(0.7 * N)]
        stage1_users = (
            stage1_group
            if len(stage1_group) <= stage1_user_count
            else random.sample(stage1_group, stage1_user_count)
        )
        votes1, decision1 = stage_voting(stage1_users, post, forfeit_bonus=0)
        sample_size += len(votes1)
        stage1_participants = [user for user, _ in votes1]

        # Check if stage 1 was conclusive (70% or more agreement)
        upvotes = sum(1 for _, vote in votes1 if vote == "upvote")
        downvotes = sum(1 for _, vote in votes1 if vote == "downvote")
        total_votes = len(votes1)

        if total_votes > 0:
            upvote_ratio = upvotes / total_votes
            downvote_ratio = downvotes / total_votes

            if upvote_ratio >= 0.7:
                votes, decision = votes1, "upvote"
            elif downvote_ratio >= 0.7:
                votes, decision = votes1, "downvote"
            else:
                # Stage 2: Top 30% of the filtered users (only if stage 1 was inconclusive)
                stage2_group = sorted_users[int(0.7 * N) :]
                stage2_users = (
                    stage2_group
                    if len(stage2_group) <= 5
                    else random.sample(stage2_group, 5)
                )
                votes2, decision2 = stage_voting(stage2_users, post, forfeit_bonus=0)
                sample_size += len(votes2)
                votes, decision = votes2, decision2
                stage2_participants = [user for user, _ in votes2]
        else:
            votes, decision = votes1, decision1

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
            low_elo_participants = [user for user, _ in special_votes]
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

    return (
        votes,
        decision,
        sample_size,
        stage1_participants,
        stage2_participants,
        low_elo_participants,
    )


def run_simulation():
    posts_per_user = 2  # Approximate a more realistic tweet-like frequency
    max_population = 5000

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

        # Track participants count from each group
        stage1_participants_count = []
        stage2_participants_count = []
        low_elo_participants_count = []

        # Track population of each group over time
        stage1_population_sizes = []
        stage2_population_sizes = []
        low_elo_population_sizes = []

        # New metrics for population sample voting
        pop_sample_total_votes = 0
        pop_sample_correct_votes = 0
        pop_sample_correct_votes_stats = []
        pop_sample_sample_sizes = []

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
                # Record group populations at this point
                filtered_users = [u for u in users if u.elo > 800]
                if not filtered_users:
                    # If no high-ELO users, consider all users as low-ELO
                    stage1_population_sizes.append(0)
                    stage2_population_sizes.append(0)
                    low_elo_population_sizes.append(len(users))
                else:
                    sorted_users = sorted(filtered_users, key=lambda u: u.elo)
                    # Stage 1: Bottom 70%
                    stage1_group_size = int(0.7 * len(sorted_users))
                    # Stage 2: Top 30%
                    stage2_group_size = len(sorted_users) - stage1_group_size
                    # Low ELO: Users with ELO <= 800
                    low_elo_group_size = len(users) - len(filtered_users)

                    stage1_population_sizes.append(stage1_group_size)
                    stage2_population_sizes.append(stage2_group_size)
                    low_elo_population_sizes.append(low_elo_group_size)

                # Regular staged voting
                (
                    votes,
                    decision,
                    post_sample_size,
                    stage1_participants,
                    stage2_participants,
                    low_elo_participants,
                ) = multi_stage_voting(post, users)
                total_votes += 1  # Count one final decision per post

                # Store participants count from each group
                stage1_participants_count.append(len(stage1_participants))
                stage2_participants_count.append(len(stage2_participants))
                low_elo_participants_count.append(len(low_elo_participants))

                is_correct = (decision == "upvote" and post.quality >= 0.5) or (
                    decision == "downvote" and post.quality < 0.5
                )

                if is_correct:
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

                # All-users voting stage
                all_votes, all_decision, all_post_sample_size = (
                    population_sample_voting(post, users)
                )
                pop_sample_total_votes += 1

                if (all_decision == "upvote" and post.quality >= 0.5) or (
                    all_decision == "downvote" and post.quality < 0.5
                ):
                    pop_sample_correct_votes += 1
                    pop_sample_correct_votes_stats.append(1)
                else:
                    pop_sample_correct_votes_stats.append(0)

                pop_sample_sample_sizes.append(all_post_sample_size)

            # Append the population size once per iteration
            population_sizes.append(len(users))
            pbar.update(new_count)
            pbar.set_postfix(current=len(users))
            population_increment *= 1 + growth_rate

    print(f"Number of posts upvoted through all voting: {upvoted_posts_count}")
    print(f"Number of correct votes: {correct_votes}")
    print(f"Total number of votes: {total_votes}")
    print(f"Correct votes: {(correct_votes / total_votes) * 100:.2f}%")
    print("\nPopulation sample voting statistics:")
    print(f"Number of correct votes: {pop_sample_correct_votes}")
    print(f"Total number of votes: {pop_sample_total_votes}")
    print(
        f"Correct votes: {(pop_sample_correct_votes / pop_sample_total_votes) * 100:.2f}%"
    )

    plot_distributions(
        users,
        upvoted_posts_quality,
        correct_votes_stats,
        population_sizes,
        sample_sizes,
        cumulative_votes_list,
        pop_sample_correct_votes_stats,
        pop_sample_sample_sizes,
        stage1_participants_count,
        stage2_participants_count,
        low_elo_participants_count,
        stage1_population_sizes,
        stage2_population_sizes,
        low_elo_population_sizes,
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
    pop_sample_correct_votes_stats,
    pop_sample_sample_sizes,
    stage1_participants_count,
    stage2_participants_count,
    low_elo_participants_count,
    stage1_population_sizes,
    stage2_population_sizes,
    low_elo_population_sizes,
):
    plt.figure(figsize=(15, 8))  # Adjusted figure size for 2x3 grid

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

    # Subplot 3: Comparison of Correct Votes Ratio with Linear Regression
    plt.subplot(2, 3, 3)
    if len(correct_votes_stats) > 10 and len(pop_sample_correct_votes_stats) > 10:
        if len(correct_votes_stats) < 50:
            window_size = min(10, len(correct_votes_stats))
        else:
            window_size = max(10, int(len(correct_votes_stats) / 100))

        staged_smoothed = (
            np.convolve(
                correct_votes_stats, np.ones(window_size) / window_size, mode="valid"
            )
            * 100
        )

        if len(pop_sample_correct_votes_stats) < 50:
            window_size = min(10, len(pop_sample_correct_votes_stats))
        else:
            window_size = max(10, int(len(pop_sample_correct_votes_stats) / 100))

        all_users_smoothed = (
            np.convolve(
                pop_sample_correct_votes_stats,
                np.ones(window_size) / window_size,
                mode="valid",
            )
            * 100
        )

        min_len = min(len(staged_smoothed), len(all_users_smoothed))
        x = np.arange(min_len)

        # Linear regression for staged voting
        (
            staged_slope,
            staged_intercept,
            staged_r_value,
            staged_p_value,
            staged_std_err,
        ) = st.linregress(x, staged_smoothed[:min_len])
        staged_r_squared = staged_r_value**2

        # Linear regression for population sample voting
        pop_slope, pop_intercept, pop_r_value, pop_p_value, pop_std_err = st.linregress(
            x, all_users_smoothed[:min_len]
        )
        pop_r_squared = pop_r_value**2

        # Plot original data
        plt.plot(x, staged_smoothed[:min_len], "b-", label="Staged Voting", alpha=0.5)
        plt.plot(
            x,
            all_users_smoothed[:min_len],
            "r-",
            label="Population Sample Voting",
            alpha=0.5,
        )

        # Plot regression lines
        plt.plot(
            x,
            staged_slope * x + staged_intercept,
            "b--",
        )
        plt.plot(
            x,
            pop_slope * x + pop_intercept,
            "r--",
        )

    else:
        min_len = min(len(correct_votes_stats), len(pop_sample_correct_votes_stats))
        x = np.arange(min_len)

        # Linear regression for raw data
        (
            staged_slope,
            staged_intercept,
            staged_r_value,
            staged_p_value,
            staged_std_err,
        ) = st.linregress(x, np.array(correct_votes_stats[:min_len]) * 100)
        staged_r_squared = staged_r_value**2

        pop_slope, pop_intercept, pop_r_value, pop_p_value, pop_std_err = st.linregress(
            x, np.array(pop_sample_correct_votes_stats[:min_len]) * 100
        )
        pop_r_squared = pop_r_value**2

        # Plot original data
        plt.plot(
            x,
            np.array(correct_votes_stats[:min_len]) * 100,
            "b-",
            label="Staged Voting",
            alpha=0.5,
        )
        plt.plot(
            x,
            np.array(pop_sample_correct_votes_stats[:min_len]) * 100,
            "r-",
            label="Population Sample Voting",
            alpha=0.5,
        )

        # Plot regression lines
        plt.plot(
            x,
            staged_slope * x + staged_intercept,
            "b--",
            label=f"Staged Regression (R²={staged_r_squared:.3f})",
        )
        plt.plot(
            x,
            pop_slope * x + pop_intercept,
            "r--",
            label=f"Pop Sample Regression (R²={pop_r_squared:.3f})",
        )

    plt.title("Comparison of Correct Votes Ratio")
    plt.xlabel("Stage Index")
    plt.ylabel("Proportion of Correct Votes (%)")
    plt.ylim(0, 110)
    plt.grid(True)
    plt.legend()

    # Subplot 4: Population Over Time
    plt.subplot(2, 3, 4)
    plt.plot(range(len(population_sizes)), population_sizes, label="Population Size")
    plt.xlabel("Stage Index")
    plt.ylabel("Population Size")
    plt.title("Population Over Time")

    # Subplot 5: Sample Size Used Over Time
    plt.subplot(2, 3, 5)
    plt.plot(range(len(sample_sizes)), sample_sizes, color="g", label="Staged Voting")
    plt.plot(
        range(len(pop_sample_sample_sizes)),
        pop_sample_sample_sizes,
        color="r",
        label="Population Sample Voting",
    )
    plt.xlabel("Stage Index")
    plt.ylabel("Number of Voters")
    plt.title("Sample Size Used Over Time")
    plt.legend()

    # Subplot 6: Voting Participation Ratio Over Time (by user group)
    plt.subplot(2, 3, 6)

    # Use a moving window to smooth the data
    window_size = min(50, len(cumulative_votes_list))
    if window_size > 0:
        # Process with a moving average
        stage1_ratio = []
        stage2_ratio = []
        low_elo_ratio = []

        for i in range(len(cumulative_votes_list) - window_size + 1):
            # Average group sizes over the window
            window_stage1_pop = (
                sum(stage1_population_sizes[i : i + window_size]) / window_size
            )
            window_stage2_pop = (
                sum(stage2_population_sizes[i : i + window_size]) / window_size
            )
            window_low_elo_pop = (
                sum(low_elo_population_sizes[i : i + window_size]) / window_size
            )

            # Sum of participants in this window
            window_stage1_votes = sum(stage1_participants_count[i : i + window_size])
            window_stage2_votes = sum(stage2_participants_count[i : i + window_size])
            window_low_elo_votes = sum(low_elo_participants_count[i : i + window_size])

            # Calculate the vote frequency: votes per user in each group
            # This accounts for population growth by normalizing by the population size
            if window_stage1_pop > 0:
                stage1_ratio.append(
                    (window_stage1_votes / window_stage1_pop) * 100 / window_size
                )
            else:
                stage1_ratio.append(0)

            if window_stage2_pop > 0:
                stage2_ratio.append(
                    (window_stage2_votes / window_stage2_pop) * 100 / window_size
                )
            else:
                stage2_ratio.append(0)

            if window_low_elo_pop > 0:
                low_elo_ratio.append(
                    (window_low_elo_votes / window_low_elo_pop) * 100 / window_size
                )
            else:
                low_elo_ratio.append(0)

        # Plot the ratios
        x_range = range(len(stage1_ratio))
        plt.plot(x_range, stage1_ratio, "b-", label="Stage 1 Users (Bottom 70%)")
        plt.plot(x_range, stage2_ratio, "r-", label="Stage 2 Users (Top 30%)")
        plt.plot(x_range, low_elo_ratio, "g-", label="Low-ELO Users (≤800)")

    plt.xlabel("Stage Index")
    plt.ylabel("Vote Frequency (% of users voting per round)")
    plt.title("Voting Frequency by User Group")
    plt.legend()

    plt.tight_layout()
    plt.show()


users = run_simulation()
