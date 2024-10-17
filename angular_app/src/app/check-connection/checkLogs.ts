export class checkLogs{
  constructor(
    public ranCheck : number,
    public plateName : string,
    public Channel : number,
    public Stimulating : number,
    public harvardAparatus : number,
    public current : number,
    
  ){
    this.ranCheck = ranCheck
    this.plateName = plateName
    this.Channel = Channel
    this.Stimulating = Stimulating
    this.harvardAparatus = harvardAparatus
    this.current = current
  }
}