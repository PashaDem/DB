# DATA MODELS AND DATABASE MANAGEMENT SYSTEMS
## Demeshkevich Pavel Andreevich, 153501
### Cleaning service - Cleanix

### Used technologies

- FastAPI application
- PostgreSQL database
- aiosql wrapper over asyncpg database driver

### Functional requirements

- Crud operations over Entities: Companies, Feedbacks, Transports, Clients, Orders, Tools, Employees and Services
- Client Authentication through JSON WEB TOKENS
- Role-based authorization system with three possible roles (Client, Employee, Manager)
- Collecting statistics about users activity
- Three-staged order-processing
-------------------------------

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
