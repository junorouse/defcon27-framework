# exploit task worker

## implementation

```
                                      read config file
                                      execute celery task
+----------------+                  +----------------+               +----------------+
|      node      |   change config  |                |               |  celery        |
|   (dashboard   +---file---------->+     go.py      <--------------->  with redis    |
|    framework)  |                  |                |               |  (broker / be) |
+----------------+                  +----------------+               +----------------+


go.py under multi process
```

## dependencies

- celery
- celery-flower (web maanger client)


# Run

```sh
export CONF_PATH={CONF_PATH}
SETTING_PATH=basic_settings.py ./go.py
```

- conf_example.json

```json
{
    "team_info": [
        {"name": "PPP", "host": "1.2.3.4"},
        {"name": "QQQ", "host": "1.2.3.4"},
    ],
    "exploit": [
        {
            "name": "prob1",
            "port": 1234,
            "teams": [
                    {"name": "PPP", "priority": [{"name": "ex1", "max_try": 5}]},
                    {
                        "name": "QQQ", 
                        "priority": [
                                        {"name": "ex2", "max_try": 5}, 
                                        {"name": "ex1", "max_try": 5}
                                    ]
                    }
            ]
        }
    ]
}
```
