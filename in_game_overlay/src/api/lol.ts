export const getWinrate = async (): Promise<any> =>
  (await fetch(`http://127.0.0.1:7998/`)).json();
