import React, { useState } from 'react';

const App = () => {
  // Replace with your own letters, or create a function to set them
  const [letters, setLetters] = useState(Array(16).fill(''));
  const [errorMessage, setErrorMessage] = useState('');
  const [comb, setComb] = useState([[]]);
  const [allLetterPossibility, setAllLetterPossibility] = useState(true);
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [projScores, setProjScores] = useState([]);

  const handleInputChange = (index, value) => {
    // This function now only updates the letters state.
    const newLetters = [...letters];
    newLetters[index] = value.slice(0, 3).toLowerCase(); // Keep "qu" or any single letter.
    setLetters(newLetters);
  };

  const handleKeyDown = (index, event) => {
    // Handle special key down events here, such as detecting 'Shift' + character.
    if (event.key.length === 1 && !event.shiftKey) { // A single character is pressed without Shift.
      if (index < letters.length - 1) {
        setTimeout(() => document.getElementById(`tile-${index + 1}`).focus(), 0); // Move focus to the next tile.
      }
    }

    // Additional condition for handling backspace to move to the previous tile, if needed.
    if (event.key === "Backspace" && letters[index] === '' && index > 0) {
      setTimeout(() => document.getElementById(`tile-${index - 1}`).focus(), 0);
    }
  };

  const prepareBoard = () => {
    let board = [];
    for (let i = 0; i < 4; i++) {
      // Use map to convert each letter to lowercase before adding it to the board
      board.push(letters.slice(i * 4, (i + 1) * 4).map(letter => letter.toLowerCase()));
    }
    return board;
  };

  const solvePuzzle = () => {
    const board = prepareBoard();
    fetch('/api/find-words', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ board }),
    })
      .then(response => {
        console.log(response)
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        console.log(data);
        console.log(letters);
        setComb(data.comb);
        setAllLetterPossibility(data.allclear);
        setCurrentWordIndex(0);
        setProjScores(data.proj);
      })
      .catch((error) => {
        console.error('Error:', error);
        setErrorMessage('Failed to solve puzzle. Please try again.');
      });
  };

  const currentPath = comb[currentWordIndex] ? comb[currentWordIndex][1] : [];
  const findOrderInPath = (row, col) => {
    return comb[currentWordIndex][1] ? currentPath.findIndex(([r, c]) => r === row && c === col) : -1;
  };
  const goToPrevWord = () => {
    setCurrentWordIndex((currentWordIndex - 1) % comb.length);
  };
  const goToNextWord = () => {
    setCurrentWordIndex((currentWordIndex + 1) % comb.length);
  };



  // Function to handle the Reset button click
  const resetPuzzle = () => {
    setLetters(Array(16).fill(''));
    setComb([[]]);
    setAllLetterPossibility(true);
    setCurrentWordIndex(0);
    setProjScores([]);
  };

  return (
    <div className="game-container">
      <span className="scores">
        {projScores.map((score, idx) => (
          <span> Projected Score for using {(idx + 1) * 10} words: {score}</span>
        ))}
      </span>
      <span style={{ fontSize: '30px', color: "white" }}>All letter possibility: {allLetterPossibility ? "POSSIBLE" : "IMPOSSIBLE"}</span>
      <span style={{ fontSize: '30px', color: "white" }}>{comb[currentWordIndex][0]} {comb[currentWordIndex][2]}</span>

      <div className="grid">
        {letters.map((letter, index) => {
          const row = Math.floor(index / 4);
          const col = index % 4;
          const order = findOrderInPath(row, col);
          const isPartOfWord = order !== -1;
          const isStartingCell = order === 0;
          const cellStyle = isStartingCell ? { backgroundColor: 'orange' } : isPartOfWord ? { backgroundColor: 'black' } : {};
          const orderStyle = { top: '0', right: '0', fontSize: '30px' };
          const style = { outline: 'none', width: '100%', padding: '0px', border: 'none', textAlign: 'center', fontSize: '30px' }
          return (
            <div key={index} className="grid-item" style={cellStyle}>
              {isPartOfWord && <span style={orderStyle}>{order + 1}</span>}
              <input
                key={index}
                id={`tile-${index}`}
                type="text"
                maxLength="3"
                value={letter}
                style={style}
                onChange={(e) => handleInputChange(index, e.target.value)}
                onKeyDown={(e) => handleKeyDown(index, e)}
              />
            </div>
          );
        })}
      </div>
      <div className="buttons">
        <button onClick={resetPuzzle} className="button reset">RESET</button>
        <button onClick={solvePuzzle} className="button solve">SOLVE</button>
        {comb.length > 0 && (
          <><button style={{ backgroundColor: "black" }} onClick={goToPrevWord} className="button prev">PREV</button>
            <button style={{ color: "black" }} onClick={goToNextWord} className="button next">NEXT</button></>
        )}
      </div>
    </div >
  );
}
export default App;
