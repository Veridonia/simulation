import random
import numpy as np
import matplotlib.pyplot as plt
from termcolor import colored
from tqdm import tqdm

class User:
    def __init__(self, id, elo=800):
        self.id = id
        self.elo = elo
        self.goodness = self.generate_goodness()
        self.mood_factor = random.uniform(0, 0.1)  # Random value from 0 to 0.1
        self.adjusted_goodness = self.goodness

    def generate_goodness(self):
        goodness = 1 - np.random.exponential(scale=0.3)  # Adjusted scale to 0.3
        while goodness < 0:
            goodness = 1 - np.random.exponential(scale=0.3)
        return goodness

    def apply_mood(self):
        self.adjusted_goodness = self.goodness
        if random.random() < self.mood_factor:
            adjustment = random.uniform(0, 0.25)
            if random.choice([True, False]):
                self.adjusted_goodness = min(1, self.goodness * (1 + adjustment))  # Increase goodness by 0% to 25%
            else:
                self.adjusted_goodness = max(0, self.goodness * (1 - adjustment))  # Decrease goodness by 0% to 25%

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
        vote_decision = 'upvote' if random.uniform(0, 1) < user.adjusted_goodness else random.choice(['downvote', 'upvote'])
    else:
        vote_decision = 'downvote' if random.uniform(0, 1) < user.adjusted_goodness else random.choice(['downvote', 'upvote'])
    return vote_decision

def stage_voting(stage_users, post, forfeit_bonus=5):
    votes = []
    stage_decision = 'draw'
    for user in stage_users:
        vote_decision = vote(user, post)
        votes.append((user, vote_decision))

    upvotes = [user for user, vote in votes if vote == 'upvote']
    downvotes = [user for user, vote in votes if vote == 'downvote']

    if not upvotes and downvotes:
        winning_team = downvotes
        losing_team = upvotes
        stage_decision = 'downvote'
    elif not downvotes and upvotes:
        winning_team = upvotes
        losing_team = downvotes
        stage_decision = 'upvote'
    elif len(upvotes) > len(downvotes):
        winning_team = upvotes
        losing_team = downvotes
        stage_decision = 'upvote'
    elif len(downvotes) > len(upvotes):
        winning_team = downvotes
        losing_team = upvotes
        stage_decision = 'downvote'
    else:
        return votes, stage_decision

    if not losing_team:
        # Forfeit case: Winning team gets a small fixed number of points
        for user in winning_team:
            user.elo += forfeit_bonus
    else:
        average_winner_elo = sum(user.elo for user in winning_team) / len(winning_team)
        average_loser_elo = sum(user.elo for user in losing_team) / len(losing_team)

        change_per_winner, change_per_loser = elo_update_team(
            average_winner_elo, average_loser_elo, k=32, 
            winner_size=len(winning_team), loser_size=len(losing_team)
        )

        for user in winning_team:
            user.elo += change_per_winner
        for user in losing_team:
            user.elo -= change_per_loser

    return votes, stage_decision

def elo_update_team(winner_avg_elo, loser_avg_elo, k=32, winner_size=1, loser_size=1):
    expected_score_winner = 1 / (1 + 10 ** ((loser_avg_elo - winner_avg_elo) / 400))
    expected_score_loser = 1 - expected_score_winner
    change_winner = k * (1 - expected_score_winner)
    change_loser = k * (0 - expected_score_winner)
    
    change_per_winner = change_winner / winner_size
    change_per_loser = abs(change_loser / loser_size)
    
    return change_per_winner, change_per_loser

def vote(user, post):
    user.apply_mood()  # Update adjusted goodness before voting
    if post.quality >= 0.5:
        vote_decision = 'upvote' if random.uniform(0, 1) < user.adjusted_goodness else random.choice(['downvote', 'upvote'])
    else:
        vote_decision = 'downvote' if random.uniform(0, 1) < user.adjusted_goodness else random.choice(['downvote', 'upvote'])
    return vote_decision

def run_simulation(n_users, n_posts):
    users = [User(i) for i in range(n_users)]
    posts = [Post(i) for i in range(n_posts)]
    upvoted_posts_quality = []
    upvoted_posts_count = 0
    total_votes = 0
    correct_votes = 0
    votes_stats = []

    # Initialize the progress bar
    pbar = tqdm(total=len(posts), desc="Processing items")

    for post in posts:
        sorted_users = sorted(users, key=lambda x: x.elo)
        
        # Stage 1 voting
        stage1_candidates = sorted_users[:len(users) // 2]
        num_stage1_users = min(10, max(1, len(stage1_candidates) // 100))
        stage1_users = random.sample(stage1_candidates, num_stage1_users)
        stage1_votes, stage1_decision = stage_voting(stage1_users, post)
        total_votes += 1

        pbar.update(1)

        if stage1_decision == 'upvote' and post.quality >= 0.5 or stage1_decision == 'downvote' and post.quality < 0.5:
            correct_votes += 1

        votes_stats.append((1, post, stage1_votes, stage1_decision))

        if stage1_decision != 'upvote':
            continue  # Skip to the next post if majority vote is not 'upvote'

        # Stage 2 voting
        stage2_candidates = sorted_users[len(users) // 2 : int(len(users) * 0.8)]
        num_stage2_users = min(10, max(1, len(stage2_candidates) // 100))
        stage2_users = random.sample(stage2_candidates, num_stage2_users)
        stage2_votes, stage2_decision = stage_voting(stage2_users, post)
        total_votes += 1

        if stage2_decision == 'upvote' and post.quality >= 0.5 or stage2_decision == 'downvote' and post.quality < 0.5:
            correct_votes += 1

        votes_stats.append((2, post, stage2_votes, stage2_decision))

        if stage2_decision != 'upvote':
            continue  # Skip to the next post if majority vote is not 'upvote'

        # Stage 3 voting
        stage3_candidates = sorted_users[int(len(users) * 0.8):]
        num_stage3_users = min(10, max(1, len(stage3_candidates) // 100))
        stage3_users = random.sample(stage3_candidates, num_stage3_users)
        stage3_votes, stage3_decision = stage_voting(stage3_users, post)
        total_votes += 1

        if stage3_decision == 'upvote' and post.quality >= 0.5 or stage3_decision == 'downvote' and post.quality < 0.5:
            correct_votes += 1

        votes_stats.append((3, post, stage3_votes, stage3_decision))

        if stage3_decision == 'upvote':
            upvoted_posts_count += 1
            upvoted_posts_quality.append(post.quality)

        if len(votes_stats) > 10:
            votes_stats = votes_stats[-10:]

    for vote_stat in votes_stats:
        printStageResult(*vote_stat)

    print(f"Number of posts upvoted through all 3 stages: {upvoted_posts_count}")
    print(f"Number of posts upvoted through all 3 stages (percent): {(upvoted_posts_count / total_votes) * 100:.2f}%")
    print(f"Number of correct votes: {correct_votes}")
    print(f"Total number of votes: {total_votes}")
    print(f"Correct vote percentage: {(correct_votes / total_votes) * 100:.2f}%")
    plot_distributions(users, upvoted_posts_quality)
    return users

def printStageResult(stage, post, votes, stage_result):
    print(f"Stage {stage} voting for Post {post.id} (Quality: {post.quality:.2f}):")
    for user, vote in votes:
        vote_colored = colored(vote, 'green' if vote == 'upvote' else 'red')
        print(f"User {user.id} (Adj. Goodness: {user.adjusted_goodness:.2f}, ELO: {user.elo:.2f}) voted {vote_colored}")
    stage1_result_colored = colored(stage_result, 'green' if stage_result == 'upvote' else 'red')
    print(f"Stage {stage} majority decision: {stage1_result_colored}\n")

def plot_distributions(users, upvoted_posts_quality):
    elo_ratings = [user.elo for user in users]
    goodness_factors = [user.goodness for user in users]

    plt.figure(figsize=(18, 6))

    plt.subplot(1, 3, 1)
    plt.yscale('log')
    plt.hist(elo_ratings, bins=100, edgecolor='black')
    plt.xlabel('Elo Rating')
    plt.ylabel('Number of Users')
    plt.title('Distribution of Users by Elo Rating')

    plt.subplot(1, 3, 2)
    plt.hist(goodness_factors, bins=100, edgecolor='black')
    plt.xlabel('Goodness Factor')
    plt.ylabel('Number of Users')
    plt.title('Distribution of Users by Goodness Factor')

    plt.subplot(1, 3, 3)
    plt.hist(upvoted_posts_quality, bins=50, edgecolor='black')
    plt.xlabel('Post Quality')
    plt.ylabel('Number of Posts')
    plt.title('Distribution of Upvoted Posts by Quality')

    plt.tight_layout()
    plt.show()

# Parameters
n_users = 10000
n_posts = 50000

# Run simulation
users = run_simulation(n_users, n_posts)

# Plot distributions
plot_distributions(users)