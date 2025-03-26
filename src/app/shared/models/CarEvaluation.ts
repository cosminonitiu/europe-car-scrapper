export interface CarEvaluationBuyer {'date_purchased': string, 'user_id': string}

export interface CarEvaluation {
  'Additional Info': string,
  'Price Range': {
    'Max': number,
    'Min': number
  },
  'car_id': string,
  'date_purchased': string,
  'users': CarEvaluationBuyer[]
}
