import { invoke } from '@tauri-apps/api';
import {LcuMatchList,MatchList,Game} from "../interface/MatchInfo";
import {queryGameType} from "./tool";

export const getChampSelect = async () => {
  try {
    const res: { [key: string]: any } = await invoke('get_champ_select')
    return res
  } catch (e) {
    return null
  }
}

// 根据召唤师ID查询战绩
const getMatchList = async (puuid: string, begIndex: string, endIndex: string): Promise<LcuMatchList|null> => {
  try {
    const res:LcuMatchList = await invoke('get_match_list',{puuid:puuid,begIndex:begIndex,endIndex:endIndex})
    return res
  }catch (e){
    return null
  }
}

const timestampToDate = (timestamp: number) => {
  var date = new Date(timestamp)
  return (date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1) + '-' + date.getDate()
}


// 获取简单的对局数据
const getSimpleMatch = (match: Game,gameModel:string):MatchList => {
  return {
    gameId: String(match.gameId),
    champId: String(match.participants[0].championId),
    // 是否取得胜利
    isWin: match.participants[0].stats.win === true ? true : false,
    // 击杀数目
    kills: match.participants[0].stats.kills,
    // 死亡数目
    deaths: match.participants[0].stats.deaths,
    // 助攻数目
    assists: match.participants[0].stats.assists,
    // 游戏时间
    matchTime: timestampToDate(match.gameCreation),
    // 游戏模式
    gameModel:gameModel
  }
}

// 处理战绩数据
export const queryMatchList = async (puuid: string, begIndex: string, endIndex: string):Promise<MatchList[] | []>  => {
  const matchList = await getMatchList(puuid, begIndex, endIndex)

  if (matchList === null) {return []}

  if (matchList?.games?.games?.length === 0 || matchList?.games?.games === undefined ) {return []}

  const simpleMatchList:MatchList[] = []
  for (const matchListElement of isRevGames(matchList.games.games)) {
    const gameModel = queryGameType(matchListElement.queueId)
    simpleMatchList.push(getSimpleMatch(matchListElement,gameModel))
  }

  return simpleMatchList
}

const isRevGames = (games:Game[]):Game[]  =>  {
  const len = games.length
  if (games[0].gameCreation > games[len-1].gameCreation) {
    return games
  }else {
    return games.reverse()
  }
}
