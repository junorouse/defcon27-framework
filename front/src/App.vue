<template>
  <div>
  <div class="row" style="padding:10px; margin-left: 10px;">
    <h2>chall name</h2><input type="text" v-model="juno.name" style="display: inline; width: 200px; height: 40px;"/>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <div>
      port: <input type="text" class="form-control" v-model.number="juno.port"/>
    </div>
    <div>
      <input type="text" v-model="ex_name" placeholder="exploit name">
      <input type="text" v-model.number="ex_index" placeholder="at index">
      <input type="text" v-model.number="ex_max_retry" placeholder="max_retry"><br>
      is_test: <input type="checkbox" v-model="ex_is_test" style="display: inline; width: 25px;"/>
      <br>

      <button class="btn btn-secondary button" @click="add">Add All</button>
      <button class="btn btn-secondary button" @click="editEx">Edit All</button>
      <button class="btn btn-secondary button" @click="deleteEx">Delete All</button>
      <button class="btn btn-secondary button" @click="goLoad">Load</button>
      <button class="btn btn-secondary button" @click="goInit">Init</button>
      <button class="btn btn-success button" @click="goSave">Save</button>
      <button class="btn btn-warning button" @click="getChalls">load challs</button>
    </div>
    <div style="display: inline-block;">
      <ul style="list-style-type:none">
        <li v-for="(chall, index) in challs" :key="`chall-${index}`" @click="loadChall" style="border: 1px solid red; padding: 5px; cursor: pointer;">{{ chall.name }}</li>
      </ul>
    </div>
  </div>
  <hr>

  <div class="rowx" style="margin-left: 10px; overflow-x: scroll; width: 100%; border: 2px solid red;">
    <div style="margin-right: 15px; display: inline-block;"
    v-for="(x) in juno.teams"
    :key="x">
      <h3>{{ x.name }} {{ draggingInfo }}</h3>

      <draggable tag="ul" :list="x.priority" class="list-group">
        <div
          class="list-group-item"
          v-for="(element) in x.priority"
          :key="element.name"
          style="padding: 5px; width: 300px; display: inline-block;"
        >

          <span class="text">{{ element.name }} </span>
          <input type="text" v-model.number="element.max_try" style="display: inline; width: 30px;"/>
          <input type="checkbox" v-model="element.is_test" style="display: inline; width: 25px;" />

          <!--<a @click="removeAt(element.name)">X</a>-->
        </div>
      </draggable>
    </div>

    <!--<rawDisplayer class="col-3" :value="juno" title="List" />-->
  </div>
  </div>
</template>

<script>
let id = 3;
import draggable from "vuedraggable";
export default {
  name: "handle",
  display: "Handle",
  instruction: "Drag using the handle icon",
  order: 5,
  components: {
    draggable
  },
  data() {
    return {
      // priority
      apiHost: 'http://104.248.148.118:1234',
      list: [
      ],
      juno: {
          "name": "prob1",
          "port": 1234,
          "teams": [
                  {"name": "PPP", "priority": [{"name": "ex1", "max_try": 5, "is_test": true}]},
                  {
                      "name": "QQQ",
                      "priority": [
                                      {"name": "ex2", "max_try": 5, "is_test": true},
                                      {"name": "ex1", "max_try": 5, "is_test": true}
                                  ]
                  }
          ]
      },
      ex_index: 10,
      ex_max_retry: 5,
      ex_is_test: true,
      challs: [],
      ex_name: '',
      dragging: false
    };
  },
  computed: {
    draggingInfo() {
      return this.dragging ? "under drag" : "";
    }
  },
  methods: {
    removeAt(idx) {
      alert(idx)
      this.list.splice(idx, 1);
    },
    add: function() {
      let exploitName = this.ex_name;

      // check existing
      for (let i=0; i<this.juno.teams.length; i++) {
        for (let j=0; j<this.juno.teams[i].priority.length; j++) {
          if (this.juno.teams[i].priority[j].name == exploitName) {
            alert('Already exists!')
            return;
          }
        }
      }

      let exploitAt = this.ex_index;
      let exploitMaxRetry = this.ex_max_retry;
      let exploitIsTest = this.ex_is_test;
      if (!exploitMaxRetry) exploitMaxRetry = 5;
      for (let i=0; i<this.juno.teams.length; i++) {
        this.juno.teams[i].priority.splice(exploitAt, 0, {"name": exploitName, "max_try": exploitMaxRetry, "is_test": exploitIsTest})
      }
    },
    editEx: function() {
      let exploitName = this.ex_name;
      let exploitMaxRetry = this.ex_max_retry;
      let exploitIsTest = this.ex_is_test;
      if (!exploitMaxRetry) exploitMaxRetry = 5;
      for (let i=0; i<this.juno.teams.length; i++) {
        for (let j=0; j<this.juno.teams[i].priority.length; j++) {
          if (this.juno.teams[i].priority[j].name == exploitName) {
            this.juno.teams[i].priority[j].max_try = exploitMaxRetry;
            this.juno.teams[i].priority[j].is_test = exploitIsTest;
          }
        }
      }
    },
    deleteEx: function() {
      let exploitName = this.ex_name;
      for (let i=0; i<this.juno.teams.length; i++) {
        for (let j=0; j<this.juno.teams[i].priority.length; j++) {
          if (this.juno.teams[i].priority[j].name == exploitName) {
            this.juno.teams[i].priority.splice(j, 1);
            break;
          }
        }
      }
      
    },
    goLoad: async function() {
      let challName = this.juno.name;
      try { 
      this.juno = await fetch(`${this.apiHost}/load?chall=${challName}`, {"credentials":"omit","headers":{},"body":null,"method":"GET","mode":"cors"})
      .then(response => response.json())
      } catch (e) {
        this.goInit();
        this.goSave();
        this.goLoad(); 
      }
    },
    goInit: function() {
      this.juno = {
        "name": this.juno.name,
        "port": this.juno.port,
        "teams": [
          {"name": "Ax0xE", "priority": []},
          {"name": "CGC", "priority": []},
          {"name": "HITCONxBFKinesiS", "priority": []},
          {"name": "hxp", "priority": []},
          {"name": "KaisHack GoN", "priority": []},
          {"name": "mhackeroni", "priority": []},
          {"name": "Plaid Parliament of Pwning", "priority": []},
          {"name": "r00timentary", "priority": []},
          {"name": "r3kapig", "priority": []},
          {"name": "saarsec", "priority": []},
          {"name": "Samurai", "priority": []},
          {"name": "Sauercloud", "priority": []},
          {"name": "SeoulPlusBadAss", "priority": []},
          {"name": "Shellphish", "priority": []},
          {"name": "Tea Deliverers", "priority": []},
          {"name": "TokyoWesterns", "priority": []},
        ]
      };

      /*
      for (let i=0; i<this.juno.teams.length; i++) {
        this.juno.teams[i].priority.push({"name": "ex1", "max_try": 5, "is_test": true})
        this.juno.teams[i].priority.push({"name": "ex2", "max_try": 5, "is_test": true})
      }
      */
    },
    goSave: async function() {
      let challName = this.juno.name;
      await fetch(`${this.apiHost}/save?chall=${challName}`, {"credentials":"omit","headers":{"Content-Type": "application/json"},"body":JSON.stringify(this.juno),"method":"POST","mode":"cors"})
      .then(response => response.json())

    },
    getChalls: async function() {
      this.challs = await fetch(`${this.apiHost}/challs`, {"credentials":"omit","headers":{},"body":null,"method":"GET","mode":"cors"})
      .then(response => response.json())
    },
    loadChall: function(event) {
      this.juno.name = event.target.innerText;
      this.goLoad();
    }
  }
};
</script>
<style scoped>
.button {
  margin-top: 35px;
}
.handle {
  float: left;
  padding-top: 8px;
  padding-bottom: 8px;
}
.close {
  float: right;
  padding-top: 8px;
  padding-bottom: 8px;
}
input {
  display: inline-block;
  width: 50%;
}
.text {
  margin: 20px;
}
</style>