from math import floor

def calculateCellsCount(total: int, percentages: list[float]) -> list[int]:
  fractions = [percentage * total / 100 for percentage in percentages]
  
  rounded_fractions = [floor(fraction) for fraction in fractions]
  
  error = abs(sum(fractions) - sum(rounded_fractions))
  
  if error == 0:
    return rounded_fractions

  adjustments = [
    {
        'index': index, 
        'difference': fraction - rounded_fraction
    } 
    for index, (fraction, rounded_fraction) in enumerate(zip(fractions, rounded_fractions))]
    
  adjustments.sort(key=lambda x: x['difference'], reverse=True)
  
  for i in range(floor(error)):
    rounded_fractions[adjustments[i]['index']] += 1
  
  return rounded_fractions


