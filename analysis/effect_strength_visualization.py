import pandas as pd

items = ['A1', 'A2', 'A3', 'A4']
effect_strength = [0.8, 0.6, 0.9, 0.4]

# Sort by effect strength
sorted_items = pd.DataFrame({'Item': items, 'Effect': effect_strength}).sort_values('Effect')

# Plot
plt.plot(sorted_items['Effect'], marker='o')
plt.xticks(ticks=range(len(sorted_items)), labels=sorted_items['Item'])
plt.title('Effect Strength Plot')
plt.xlabel('Items')
plt.ylabel('Effect Strength')
plt.show()