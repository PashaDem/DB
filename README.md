# DATA MODELS AND DATABASE MANAGEMENT SYSTEMS
## Radyukevich Alina Igorevna, 153502
## Cleaning company

### Functional requirements

* User authorization
* User managment (CRUD)
* Role system
* Logging user actions
* Orders managment
* Service management
* Transport management
* Statistics
* Instrument managment (CRUD)
* Feedback manegment (CRUD)

## Informological system
![image](https://github.com/Linyshka/DB/assets/92429718/d9405a2d-a7c7-4784-96ec-408040b4d01f)



## Entities
1. "Company"
  * **id** bigint, not null, PK
  * **Name** varchar, not null
  * **Type** varchar, not null
  * **Address** varchar, not null
  * **ClientId** bigint, not null -> client
2. "Feedback"
  * **id** bigint, not null, PK
  * **CreateAt** date, not null
  * **Score** int, not null
  * **Description** varchar, not null
  * **ClientId** bigint, not null -> client
3. "Statistic"
  * **id** bigint, not null, PK
  * **OrdersCount** bigint, not null
  * **Price** double, not null
  * **FeddbackCount** int, not null
  * **ClientId** bigint, not null -> client
4. "Client"
  * **id** bigint, not null, PK
  * **FullName** varchar, not null
  * **CompanyId** bigint, not null -> company
  * **Telephone** int, not null
  * **Feedbacks** bigint, not null -> feedback
  * **ClientId** bigint, not null -> client
5. "Order"
  * **id** bigint, not null, PK
  * **Services** bigint, not null -> service
  * **Transport** varchar, not null -> transport
  * **Address** varchar, not null
  * **Date** date, not null
  * **Tools** bigint, not null -> tool
  * **Feedbacks** bigint, not null -> feedback
  * **Employees** date, not null -> employee
  * **ClientId** bigint, not null -> client
6. "Transport"
  * **id** bigint, not null, PK
  * **Mark** varchar, not null
  * **OderId** bigint, not null -> order
7. "Empoyee"
  * **id** bigint, not null, PK
  * **Specialization** varchar, not null
  * **FullName** varchar, not null
  * **Experience** bigint, not null
  * **OderId** bigint, not null -> order
8. "Service"
  * **id** bigint, not null, PK
  * **Type** varchar, not null
  * **Description** date, not null
  * **OrderId** bigint, not null -> order
9. "Contract"
  * **id** bigint, not null, PK
  * **Price** double, not null
  * **OderId** bigint, not null -> order
10. "Tool"
  * **id** bigint, not null, PK
  * **Name** varchar, not null
  * **Description** date, not null
  * **OrderId** bigint, not null -> order
