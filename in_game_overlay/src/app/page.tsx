"use client";

import { useEffect, useState } from "react";
import { getWinrate } from "../api/lol";

import * as d3 from "d3";

interface NumberMap {
  [key: number]: number;
}

function drawChart(n: number, rate: NumberMap) {
  interface DataPoint {
    x: number;
    y: number;
  }

  console.log(rate);

  n = 20;

  const data: DataPoint[] = Object.entries(rate).map(
    ([k, v]: [string, string]) => ({
      x: parseInt(k),
      y: parseInt(v),
    })
  );

  let mins = 20;

  if (n > mins) {
    mins = n + 1;
  }

  const margin = { top: 20, right: 20, bottom: 40, left: 40 };
  const w = 900;
  const h = 400;
  const width = w - margin.left - margin.right;
  const height = h - margin.top - margin.bottom;

  d3.select("svg").remove();
  const svg0 = d3.select("div").append("svg");

  svg0.append("rect").attr("width", w).attr("height", h).attr("fill", "white");

  const svg = svg0
    .attr("width", w)
    .attr("height", h)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  const xScale = d3.scaleLinear().domain([0, mins]).range([0, width]);
  const yScale = d3.scaleLinear().domain([0, 100]).range([height, 0]);

  // svg
  //   .append("text")
  //   .attr("text-anchor", "end")
  //   .attr("x", width)
  //   .attr("y", height + margin.top + 20)
  //   .text("X axis title");

  // svg
  //   .append("text")
  //   .attr("text-anchor", "end")
  //   .attr("transform", "rotate(-90)")
  //   .attr("y", -margin.left + 20)
  //   .attr("x", -margin.top)
  //   .text("Y axis title");

  // Define the line
  const line = d3
    .line<DataPoint>()
    .x((d) => xScale(d.x))
    .y((d) => yScale(d.y));

  svg
    .append("path")
    .datum(data)
    .attr("fill", "none")
    .attr("stroke", "steelblue")
    .attr("stroke-width", 2)
    .attr("d", line);

  svg
    .append("g")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(xScale));

  svg.append("g").call(d3.axisLeft(yScale));
}

export default function Home() {
  const [winrate, setWinrate] = useState<{ pred: number; time: number }>({
    pred: 50,
    time: 0,
  });

  // gameTime is int starting from 0 winrate array is of length gameTime + 1
  let gameTime: number = Math.round(winrate.time);
  const [winrateMap, setWinrateMap] = useState<NumberMap>({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        const fetchedWinrate = await getWinrate();
        console.log(fetchedWinrate);
        setWinrate(fetchedWinrate);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    const interval = setInterval(fetchData, 1000);

    return () => {
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    setWinrateMap((prevWinrateArray) => ({
      ...prevWinrateArray,
      [gameTime]: winrate.pred,
    }));
  }, [winrate]);

  useEffect(() => {
    drawChart(gameTime, winrateMap);
  }, [winrateMap]);

  return (
    <div>
      {/* <p>{winrate.pred}</p> */}
      {/* <p>{winrate.time}</p> */}
    </div>
  );
}
