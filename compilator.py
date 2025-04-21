import zipfile
import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import time
#pip install matplotlib

# extract individual ballots from zip file containing all of them
# set the name of zip_path as the name of your ballot zip file
zip_path = 'Ballots_zipped.zip'
extract_path = 'unzipped_html_files'

if not os.path.exists(extract_path) or not os.listdir(extract_path):
    print("Extracting files...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
else:
    print("Files already extracted, skipping unzip.")

# write the names of the candidate in candidate_pool and make sure they are correctly spelled and in lower case
# *********************************************
candidate_pool = ["victoria", "erik", "cedric"]
# *********************************************
candidate_pool = [name.lower() for name in candidate_pool]

# read ballots into ranked lists
ballots = []
all_candidates = set(candidate_pool)

#reads individual files and finds ranking of the names
for idx, filename in enumerate(sorted(os.listdir(extract_path))):
    if filename.endswith('.html'):
        file_path = os.path.join(extract_path, filename)
        try:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as file:
                    content = file.read()

            content = content.lower()
            ranked_names = []

            for name in candidate_pool:
                index = content.find(name)
                if index != -1:
                    ranked_names.append((index, name))

            ranked_names.sort()
            ranked_names = [name for _, name in ranked_names]
            if ranked_names:
                print(f"Ballot {idx + 1}: First choice is {ranked_names[0]}")
                ballots.append(ranked_names)

        except Exception as e:
            print(f"Error reading {filename}: {e}")

# voting functions
def count_first_place(ballots, all_candidates):
    vote_counts = {name: 0 for name in all_candidates}
    for ballot in ballots:
        for name in ballot:
            if name in all_candidates:
                vote_counts[name] += 1
                break
    return vote_counts

# visualization setup
def animate_votes(bar_ax, text_ax, names, old_vals, new_vals, round_history, round_num):
    max_y = max(max(old_vals), max(new_vals), 10) + 50
    num_frames = 30
    for frame in range(1, num_frames + 1):
        bar_ax.cla()
        text_ax.cla()
        text_ax.axis('off')

        intermediate_vals = [
            old + (new - old) * frame / num_frames
            for old, new in zip(old_vals, new_vals)
        ]
        bars = bar_ax.bar(names, intermediate_vals, color='purple')
        bar_ax.set_title(f"Round {round_num} - Current Vote Count")
        bar_ax.set_ylabel("Votes")
        bar_ax.set_ylim(0, max_y)

        for i, bar in enumerate(bars):
            bar_ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
                        f"{int(intermediate_vals[i])}", ha='center', va='bottom')

        full_text = "\n\n".join(round_history)
        text_ax.text(0, 1, full_text, fontsize=9, va='top', ha='left', family='monospace', wrap=True)

        plt.tight_layout()
        plt.pause(0.03)

# voting loop with visualization
plt.ion()
candidates_left = set(all_candidates)
prev_votes = {name: 0 for name in all_candidates}
round_num = 1
round_history = []

fig = plt.figure(figsize=(14, 8))
gs = gridspec.GridSpec(1, 2, width_ratios=[2.5, 1])
bar_ax = fig.add_subplot(gs[0])
text_ax = fig.add_subplot(gs[1])
text_ax.axis('off')

# logic responsible for looping until result is found
while len(candidates_left) > 1:
    vote_counts = count_first_place(ballots, all_candidates)

    print(f"Votes for round {round_num}: {vote_counts}")

    round_info = f"Round {round_num} Results:\n"
    for name, count in sorted(vote_counts.items()):
        round_info += f"  {name}: {count} votes\n"

    min_votes = min([count for name, count in vote_counts.items() if name in candidates_left])
    lowest = [name for name, count in vote_counts.items() if count == min_votes and name in candidates_left]

    if len(lowest) == len(candidates_left):
        round_info += "\nIt's a tie between remaining candidates!"
        round_history.append(round_info)

        # animate final tie round
        names = list(all_candidates)
        old_vals = [prev_votes.get(name, 0) for name in names]
        new_vals = [vote_counts.get(name, 0) for name in names]
        animate_votes(bar_ax, text_ax, names, old_vals, new_vals, round_history, round_num)
        break

    eliminated = lowest[0]
    round_info += f"\nEliminated: {eliminated}"
    round_history.append(round_info)

    # animate this round
    names = list(all_candidates)
    old_vals = [prev_votes.get(name, 0) for name in names]
    new_vals = [vote_counts.get(name, 0) for name in names]
    animate_votes(bar_ax, text_ax, names, old_vals, new_vals, round_history, round_num)

    # update for next round
    for ballot in ballots:
        if eliminated in ballot:
            ballot.remove(eliminated)
    candidates_left.remove(eliminated)
    prev_votes = vote_counts
    round_num += 1
    time.sleep(0.5)

# displaying final result
if len(candidates_left) == 1:
    winner = list(candidates_left)[0]
    final_message = f"\nWinner: {winner.upper()}"
    round_history.append(final_message)
    print(final_message)

    text_ax.cla()
    text_ax.axis('off')
    text_ax.text(0, 1, "\n\n".join(round_history), fontsize=10, va='top', ha='left', family='monospace', wrap=True)

    bar_ax.set_title(f"Winner: {winner.upper()}")
    plt.tight_layout()
    plt.ioff()
    plt.show()
else:
    plt.ioff()
    plt.show()
