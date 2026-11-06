## run python app

```sh
python app.py


```


## work with csv in grafana
```sh
# use infinity in grafana, download and import 



```
![alt text](img/1.png)


# transformation

## example - 1 - show orders table - orders
### Convert field type
![alt text](img/2.png)



### Add field from calculation
![alt text](img/3.png)


### Sort by
![alt text](img/4.png)


### Organize fields by name ( you can sort the column and rename them)
![alt text](img/5.png)

### result
![alt text](img/7.png)



## example - 2 - Revenue by City - Bar chart
### Convert field type
![alt text](img/2.png)


### Add field from calculation
![alt text](img/3.png)


### Group by
![alt text](img/6.png)

### result
![alt text](img/8.png)



## example - 3 - Revenue by Product - Pie chart
### Convert field type
![alt text](img/2.png)


### Add field from calculation
![alt text](img/3.png)


### Group by
![alt text](img/9.png)





## example - 4 - Revenue over Time per city


### Convert field type
![alt text](img/2.png)


### Add field from calculation
![alt text](img/3.png)

### Organize fields by name
![alt text](img/10.png)


### Partition by values
![alt text](img/11.png)


## example - 5 - Tehran Total Revenue
### Convert field type
![alt text](img/2.png)


### Add field from calculation
![alt text](img/3.png)


### Filter data by values
![alt text](img/12.png)

### final image
![alt text](img/13.png)



# Alerting
use this query and use script ***3-app-filter-data.py***

http://192.168.85.74:8000/sales.csv?from=${__from}&to=${__to}
