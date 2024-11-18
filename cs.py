import numpy as np
from math import gamma

def objective_Fun(x):
      return np.sum(x**2)

def init_Population(Pop_size, Dim):
      return np.random.uniform(-5,5,(Pop_size, Dim))

def Levy_Fight(beta):
      sigma = (
            gamma(1 + beta)
            * np.sin(np.pi * beta / 2)
            / (gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))
      ) ** (1 / beta)
      u = np.random.normal(0, sigma)
      v = np.random.normal(0, 1)
      step = u / abs(v) ** (1 / beta)
      return step

def CS(Obj_Fun, Pop_size = 50, Dim = 2, MaxT = 100, pa = 0.25):
      population = init_Population(Pop_size, Dim)
      finess = np.array([Obj_Fun(nest) for nest in population])
      best_solution = None
      best_finess = np.inf
      
      for i in range (MaxT):
            new_population = np.empty_like(population)
            for j, nest in enumerate(population):
                  Step_size = Levy_Fight(1.5)
                  Step_Direction = np.random.uniform(-1,1,size=Dim)
                  new_nest = nest + Step_size * Step_Direction
                  new_population[j] = new_nest
                  
                  new_population[j] = np.clip(new_population[j], -5,5)
                  
            new_finess = np.array([Obj_Fun(nest) for nest in new_population])
            
            replace_soln = np.where(new_finess < finess)[0]
            population[replace_soln] = new_population[replace_soln]
            finess[replace_soln] = new_finess[replace_soln]
            
            sort_soln = np.argsort(finess)
            population = population[sort_soln]
            finess = finess[sort_soln]
            
            if finess[0] < best_finess:
                  best_solution = population[0]
                  best_finess = finess[0]
                  
            abandon_egg = int(pa*Pop_size)
            abadon_soln = np.random.choice(Pop_size, size=abandon_egg, replace=False)
            population[abadon_soln] = init_Population(abandon_egg, Dim)
            finess[abadon_soln] = np.array([Obj_Fun(nest) for nest in population[abadon_soln]])
            
            print(f"Iteration {i+1}/{MaxT}: Best_finess = {best_finess}")
      return best_solution, best_finess


best_solution, best_finess = CS(objective_Fun) 
print("Best solution", best_solution)
print("Best finess", best_finess)