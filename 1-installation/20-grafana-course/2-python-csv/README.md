# transformation
### Add field from calculation

add two query and use random walk
![alt text](img/14.png)


### Reduce
use random walk 
![alt text](img/15.png)


### Organize fields by name
```sh
use this csv
-------------
city,product,sales,cost
Tehran,Laptop,120,90
Tehran,Phone,200,150
Isfahan,Laptop,80,60
Isfahan,Phone,150,100
Shiraz,Laptop,60,45
Shiraz,Phone,90,70
Tabriz,Laptop,70,50
Tabriz,Phone,110,85
----------------

you can rename, hide or reorder the columns
```
![alt text](img/16.png)


### Filter data by values, Sort by
```sh
use below csv
-------------
city,population,area
Tehran,9000,730
Mashhad,3400,350
Isfahan,2200,550
Karaj,1900,180
Shiraz,1800,240
Tabriz,1700,325
Qom,1300,1100
Ahvaz,1200,220
-------------


```
![alt text](img/17.png)

![alt text](img/18.png)

### Group by
```sh
use this csv
-------------
city,product,sales,cost
Tehran,Laptop,120,90
Tehran,Phone,200,150
Isfahan,Laptop,80,60
Isfahan,Phone,150,100
Shiraz,Laptop,60,45
Shiraz,Phone,90,70
Tabriz,Laptop,70,50
Tabriz,Phone,110,85
Tehran,book,300,160
----------------
```
![alt text](img/19.png)

![alt text](img/20.png)




### Join by field

```sh

dataset A
-------
city,sales_2025
Tehran,950
Isfahan,600
Shiraz,420
Tabriz,480
-------

dataset B
-------
city,sales_2026
Tehran,1100
Isfahan,640
Shiraz,510
Tabriz,450
-------

```
![alt text](img/21.png)


```sh
------------
emp_id,name,dept
1,Ali,Sales
2,Sara,IT
3,Reza,Sales
4,Neda,HR
-----------


------------
emp_id,product,amount
1,Laptop,1200
1,Phone,800
2,Monitor,300
3,Mouse,50
5,Keyboard,70
------------

```
![alt text](img/22.png)





### Merge series/tables
```sh

---------
branch,month,revenue
North,Jan,300
North,Feb,320
---------

---------
branch,month,revenue
South,Jan,250
South,Feb,270
---------

```

![alt text](img/23.png)

### Convert field type and Partition by values
```sh

---------
time,city,temp
1793491200000,Tehran,14
1793491200000,Tabriz,8
1793491200000,Shiraz,16
1793577600000,Tehran,15
1793577600000,Tabriz,7
1793577600000,Shiraz,17
1793664000000,Tehran,13
1793664000000,Tabriz,6
1793664000000,Shiraz,15

---------

```

![alt text](img/24.png)
![alt text](img/25.png)








# run python app
```sh
python app.py


```


## work with csv in grafana
```sh
# use infinity in grafana, download and import 



```
![alt text](img/1.png)



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



use this query and use script **3-app-filter-data.py**

http://192.168.85.74:8000/sales.csv?from=${__from}&to=${__to}


### geo map
```sh
------
city,lat,lon,sales
Tehran,35.69,51.39,1200
Mashhad,36.26,59.62,650
Isfahan,32.65,51.67,540
Shiraz,29.59,52.58,480
Tabriz,38.08,46.29,420
Ahvaz,31.32,48.67,300
Kerman,30.28,57.08,210
Rasht,37.28,49.58,260
Bandar Abbas,27.18,56.27,180
Kermanshah,34.31,47.07,230
------

```
![alt text](img/26.png)
![alt text](img/27.png)
![alt text](img/28.png)

