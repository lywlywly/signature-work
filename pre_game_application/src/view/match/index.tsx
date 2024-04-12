import { Image } from "@chakra-ui/react";
import type { CollapseProps } from "antd";
import { Collapse } from "antd";
import { createContext, useEffect, useState } from "react";
import { champDict } from "../../assets/champList";
import { getChampSelect, queryMatchList } from "../../utils/getMatchInfo";
import { querySumInfoBySumId, querySumRank } from "../../utils/getSumInfo";
import { getImgUrl } from "./components/MatchList";
export const AlterToSumId = createContext((sumId: number) => {});

export const Match = () => {
  const [match, setMatch] = useState<Record<string, any>>({});

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const match = await getChampSelect();
      const data = await Promise.all(
        match!["myTeam"].map(async (e: { [x: string]: any }) => {
          const sumInfo = await querySumInfoBySumId(e["summonerId"].toString());
          const sumRank = await querySumRank(e["summonerId"].toString());
          const recent = await queryMatchList(e["puuid"], "1", "5");
          const totalK = recent.reduce(
            (partialSum, a) => partialSum + a.kills,
            0
          );
          const totalD = recent.reduce(
            (partialSum, a) => partialSum + a.deaths,
            0
          );
          const totalA = recent.reduce(
            (partialSum, a) => partialSum + a.assists,
            0
          );
          return {
            e: e,
            name: sumInfo["displayName"],
            level: sumInfo["summonerLevel"],
            rank: sumRank,
            championId: e["championId"],
            totalK,
            totalD,
            totalA,
            recent: recent,
          };
        })
      );
      setMatch(data);
      console.log(data);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  console.log(match);

  const items: CollapseProps["items"] =
    match.length > 0
      ? match.map((item, index) => ({
          key: index,
          label: (
            <div className="container">
              <Image
                className="rounded"
                boxSize="40px"
                src={getImgUrl(item["championId"])}
              />
              &nbsp;&nbsp;
              <div className="text">
                <span>{item["name"]}</span>
                <br />
                <span>{item["rank"][0]}</span>
                {/* <p>Your text goes here.</p> */}
                &nbsp;
                {item.totalK}/{item.totalD}/{item.totalA}
              </div>
            </div>
          ),
          children: (
            <ul>
              {item["recent"].map((item1, index) => (
                <li key={index}>
                  <div className="container">
                    <Image
                      className="rounded"
                      boxSize="30px"
                      src={getImgUrl(item1.champId)}
                    />
                    &nbsp;
                    <div className="text">
                      {item1.isWin ? (
                        <span
                          style={{
                            color: "green",
                            fontWeight: "bold",
                            fontStyle: "italic",
                          }}
                        >
                          W
                        </span>
                      ) : (
                        <span
                          style={{
                            color: "red",
                            fontWeight: "bold",
                            fontStyle: "italic",
                          }}
                        >
                          L
                        </span>
                      )}
                      &nbsp;
                      {champDict[item1.champId].label} {item1.kills}/
                      {item1.deaths}/{item1.assists}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          ),
        }))
      : [
          {
            key: "1",
            label: "This is panel header 5",
            children: <p>{text}</p>,
          },
          {
            key: "2",
            label: "This is panel header 2",
            children: <p>{text}</p>,
          },
          {
            key: "3",
            label: "This is panel header 3",
            children: <p>{text}</p>,
          },
        ];

  const onChange = (key: string | string[]) => {
    console.log(key);
  };

  return (
    <div>
      <Collapse
        items={items}
        onChange={onChange}
        style={{ marginTop: "10px" }}
      />
    </div>
  );
};
