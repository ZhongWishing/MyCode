import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [board, setBoard] = useState([...Array(9).keys()].map(String)); // 初始矩阵
  const [algorithm, setAlgorithm] = useState("BFS"); // 算法选项
  const [moves, setMoves] = useState([]); // 计算路径
  const [isRunning, setIsRunning] = useState(false); // 动态演示状态
  const [error, setError] = useState(null); // 错误信息
  const [info, setInfo] = useState({ time: 0, pathLength: 0, nodesExplored: 0 }); // 算法运行信息

  // 判断是否可解
  const isSolvable = (state) => {
    const array = state.filter((n) => n !== "0");
    let inversions = 0;
    for (let i = 0; i < array.length; i++) {
      for (let j = i + 1; j < array.length; j++) {
        if (array[i] > array[j]) inversions++;
      }
    }
    return inversions % 2 === 0;
  };

  // 随机生成矩阵
  const generateRandomBoard = () => {
    let board;
    do {
      board = [..."123456780"].sort(() => Math.random() - 0.5);
    } while (!isSolvable(board));
    return board;
  };

  // 生成随机矩阵
  const handleGenerateRandom = () => {
    const randomBoard = generateRandomBoard();
    setBoard(randomBoard);
    setMoves([]);
    setError(null);
    setInfo({ time: 0, pathLength: 0, nodesExplored: 0 });
  };

  // 动态演示移动
  useEffect(() => {
    if (isRunning && moves.length > 0) {
      const timer = setTimeout(() => {
        setBoard(moves[0].split(""));
        setMoves((prevMoves) => prevMoves.slice(1));
      }, 300); // 调整速度（毫秒）
      return () => clearTimeout(timer);
    }
    if (isRunning && moves.length === 0) {
      setIsRunning(false); // 动画结束
    }
  }, [isRunning, moves]);

  // 处理运行算法
  const handleStart = async () => {
    setIsRunning(false);
    setError(null);
    try {
      const response = await axios.post(
          `http://127.0.0.1:5000/solve_${algorithm.toLowerCase()}`,
          {
            start: board.join(""),
          }
      );
      const { moves = [], time, path_length, nodes_explored } = response.data;
      if (moves.length === 0) throw new Error("未返回有效路径！");
      setMoves(moves);
      setInfo({ time: time.toFixed(2), pathLength: path_length, nodesExplored: nodes_explored });
      setBoard(moves[0].split(""));
      setIsRunning(true);
    } catch (err) {
      setError(err.response?.data?.error || "发生错误！");
    }
  };

  return (
      <div className="App">
        <h1>八数码问题演示</h1>
        <div className="grid">
          {board.map((num, index) => (
              <div key={index} className={`tile ${num === "0" ? "empty" : ""}`}>
                {num !== "0" ? num : ""}
              </div>
          ))}
        </div>
        <div className="controls">
          <button onClick={handleGenerateRandom}>生成随机矩阵</button>
          <select value={algorithm} onChange={(e) => setAlgorithm(e.target.value)}>
            <option value="BFS">BFS</option>
            <option value="DFS">DFS</option>
            <option value="Astar">A*</option>
            <option value="Bibfs">双向BFS</option>
            <option value="Idastar">IDA*</option>
          </select>
          <button onClick={handleStart} disabled={isRunning}>
            开始
          </button>
        </div>
        {error && <div className="error">{error}</div>}
        <div className="info">
          <p>算法运行时间：{info.time} 毫秒</p>
          <p>路径长度：{info.pathLength}</p>
          <p>遍历节点数：{info.nodesExplored}</p>
        </div>
      </div>
  );
}

export default App;
