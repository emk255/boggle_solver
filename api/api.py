from flask import Flask, request, jsonify, send_from_directory
import json, os 
app = Flask(__name__, static_folder='../boggle/build', static_url_path='')


@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')
@app.route('/api/find-words', methods=['POST'])
def find_words_endpoint():
    # with open('words_dictionary.json') as f:
    #   data = json.load(f)
    # word_list = [word for word in data.keys() if len(word) > 1]

    with open('word-list.txt') as f:
        data = f.read().split("\n")

    # with open('popular.txt') as f:
    #     data = f.read().split("\n")
    data = [d for d in data if 'an offensive word' not in d]
    word_list = [word.split(" ")[0].lower() for word in data]
    
        
    class TrieNode:
        def __init__(self):
            self.children = {}
            self.is_end_of_word = False

    class Trie:
        def __init__(self):
            self.root = TrieNode()

        def insert(self, word):
            node = self.root
            for char in word:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            node.is_end_of_word = True

        def search(self, word):
            node = self.root
            for char in word:
                if char not in node.children:
                    return False
                node = node.children[char]
            return node.is_end_of_word

        def startsWith(self, prefix):
            node = self.root
            for char in prefix:
                if char not in node.children:
                    return False
                node = node.children[char]
            return True

    def findWords(board, words):
        word_indices = {}
        def dfs(node, i, j, path, visited, indices, current_path):
            if i < 0 or i >= len(board) or j < 0 or j >= len(board[0]) or visited[i][j]:
                return
            tile = board[i][j]
            new_path = path + tile
            current_path.append((i, j))

            if not trie.startsWith(new_path):
                current_path.pop()
                return

            if trie.search(new_path):
                result.add(new_path)
                if new_path not in word_indices:
                    word_indices[new_path] = []
                word_indices[new_path].append(list(current_path))  # Store a copy of the current path

            visited[i][j] = True
            for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                dfs(node, i + dx, j + dy, new_path, visited, indices, current_path)
            visited[i][j] = False
            current_path.pop()

        trie = Trie()
        for word in words:
            trie.insert(word)

        result = set()
        visited = [[False]*4 for _ in range(4)]
        word_indices = {}  # Initialize word_indices to store all paths for each word
        for i in range(4):
            for j in range(4):
                dfs(trie.root, i, j, '', visited, [], [])  # Pass an empty list for current_path

        return list(result), word_indices  # Return both the list of found words and their paths

    def calculate_base_score(word, path):
        score = 0
        for (i,j) in path:
            score += score_chart[board[i][j]]
            if (i,j) in dl_idx:
                score+=dl_idx[(i,j)]
            if (i,j) in tl_idx:
                score+=tl_idx[(i,j)]       
        for (i,j) in dw_idx:
            if (i,j) in path:
                score*=2
        for (i,j) in tw_idx:
            if (i,j) in path:
                score*=3
        if len(word) >=5:
            score +=(len(word)-4)*5
        return score


    score_chart = {
    'a':1, 'b':3, 'c':3, 'd':2, 'e':1, 'f':4, 'g':2, 'h':4, 'i':1, 'j':8, 'k':5, 'l':1, 'm':3, 'n':1, 'o':1,'p':3,
    'q':10, 'r':1, 's':1, 't':1, 'u':1, 'v':4, 'w':4, 'x':8, 'y':4, 'z':10, 'qu':10
}
    data = request.json
    board = data.get('board', [])  
    if len(board) != 4 or any(len(row) != 4 for row in board):
        return jsonify({"error": "Invalid board size"}), 400
    dl_idx, tl_idx, dw_idx, tw_idx = {}, {}, [], []
    for i in range(4):
        for j in range(4):
            if '2' in board[i][j]:
                dl_idx[(i,j)] = score_chart[board[i][j].split("2")[0]]
                board[i][j] = board[i][j].split("2")[0]
            if'3' in board[i][j]:
                tl_idx[(i,j)] = score_chart[board[i][j].split("3")[0]]*2
                board[i][j] = board[i][j].split("3")[0]
            if '4' in board[i][j]:
                dw_idx.append((i,j))
                board[i][j] = board[i][j][0]
            if '5' in board[i][j]:
                tw_idx.append((i,j))
                board[i][j] = board[i][j][0]

    found_words, word_indices = findWords(board, word_list)

    comb = [] # list of (word, unqiue path, score)
    for word in word_indices:
        for path in word_indices[word]:
            comb.append((word, path, calculate_base_score(word, path)))
    # comb = [(a,b,c) for (a,b,c) in comb if len(a) >= 3]        
    # print(sorted_comb)
    # sorted_scores = sorted(d.items(), key=lambda item: item[1], reverse = True)
    # word_indices = {item[0]: word_indices[item[0]] for item in sorted_scores}
    # word_indices = [(key, word_indices[key]) for key in word_indices]

    covered_tiles = set()
    selected = []
    unused_comb = comb[:]
    previous_covered_count = 0
    tiles = [(i,j) for i in range(4) for j in range(4)]
    allclear_possibility = True
    while len(covered_tiles) < 16 and unused_comb:
    #     print(allclear_possibility)
        uncovered_tiles = [point for point in tiles if point not in covered_tiles]
        unused_comb.sort(key=lambda x: (len(set(x[1]) & covered_tiles), -x[2]))
        next_comb = unused_comb[0]
    #     for word in unused_comb:
    #             print(word, len(set(word[1]) & covered_tiles))
        new_covered_count = len(covered_tiles.union(set(next_comb[1])))
        if new_covered_count == previous_covered_count:
            change = False
            for comb in unused_comb:
                for (i,j) in uncovered_tiles:  
                    if (i,j) in comb[1]:
                        next_comb = comb
                        change = True
                        break
            if not change:
                allclear_possibility = False
                break
        # allclear.append(allclear_possibility)
        selected.append(next_comb)
        covered_tiles.update(next_comb[1])
        previous_covered_count = new_covered_count

        # Remove this word from future consideration
        unused_comb = [word for word in unused_comb if word[0] != next_comb[0]]
    # print(len(covered_tiles))
    # print(selected)
    # print("="*20)

    sorted_comb = sorted(unused_comb, key=lambda x: (-x[2])) # sort by descending score
    # print(sorted_comb)
    selected_words = [w for (w,_,_) in selected]
    # Step 3: Continue with descending score selection for any remaining words
    if len(covered_tiles) < 16 or len(selected_words) < len(sorted_comb):
        for word in sorted_comb:
    #         print(word, "\n")
            if word[0] not in selected_words:
                selected_words.append(word[0])
                selected.append(word)
    if len(covered_tiles) != 16:
        allclear_possibility = False

    proj_scores = []
    for n in [10,20,30,40,50]:
        if allclear_possibility:
            s = 100
        else:
            s = 0
        s += sum(score for _,_,score in selected[:n])
        proj_scores.append(s)
    return jsonify(
       { 'comb' : selected,
        'allclear': allclear_possibility,
        'proj' : proj_scores
      })

if __name__ == '__main__':
    app.run(debug=True, port=8080)