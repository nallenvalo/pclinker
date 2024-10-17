export class shortedHarvard{
    constructor(
        public Stimulator : number,
        public voltage : number,
        public stimFreq : number,
        public pulseOn : number,
      
    ){
        this.Stimulator = Stimulator
        this.voltage = voltage
        this.stimFreq = stimFreq
        this.pulseOn = pulseOn
    }
  }