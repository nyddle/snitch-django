function SnitchEvent(id, message, type, app, timestamp) {
    var self = this;
    self.id = id;
    self.message = message;
    self.type = type;
    self.app = app;
    self.timestamp = timestamp;
    self.checked = false;
}

function SnitchApp(name, selected) {
    var self = this;
    self.name = name;
    self.isSelected = ko.computed(function(){
        return self === selected();
    }, self);
}

function SnitchEventsViewsModel() {
    var self = this,
        app_url = '/web/index/';

    self.activeApp = ko.observable();
    self.apps = ko.observableArray([new SnitchApp('All', self.activeApp)]);

    self.filter = {'oloolo': 'ololo'};

    self.events = ko.observableArray([]);
    self.checkedEvents = ko.observableArray([]);

    self.showFormControls = ko.observable(false);

    self.changeApp = function(app) {
        self.activeApp(app);
        $.ajax(app_url + app.name, {
            data: JSON.stringify(self.filter),
            contentType: "application/json",
            type: 'POST'
        });
    };

    self.checkedEvents.subscribe(function () {
        if (self.checkedEvents().length > 0) {
            self.showFormControls(true);
        } else {
            self.showFormControls(false);
        }
    });

    self.showEvents = ko.computed(function () {
        return self.events();
    }, self);

    self.checkEvent = function (event) {
        var index = self.checkedEvents.indexOf(event);
        if (index > -1) {
            self.checkedEvents.remove(event);
        } else {
            self.checkedEvents.push(event);
        }
        self.checkedEvents.valueHasMutated();
        return true;
    };

    self.checkAll = function () {
        self.checkedEvents(self.events());
        $('.event-chbx').prop('checked', true);
        return false;
    };

    self.uncheckAll = function () {
        self.checkedEvents([]);
        $('.event-chbx').prop('checked', false);
        return false;
    };

    self.removeEvents = function () {
        self.checkedEvents().forEach(function (event) {
            self.events.remove(event);
        });
        // todo: api call
        self.checkedEvents([]);
    };
}

$(function () {
    var model = new SnitchEventsViewsModel();
    $.post('/web/index',function (response) {
        for (var i = 0; i < response.events.length; i++) {
            var event = response.events[i];
            model.events.push(new SnitchEvent(1, event.message, event.type, event.app, event.timestamp));
        }
        for (var j = 0; j < response.apps.length; j++) {
            console.log(response.apps[j])
            model.apps.push(new SnitchApp(response.apps[j], model.activeApp));
        }
        model.activeApp(model.apps()[0]);
        model.apps.valueHasMutated();
        ko.applyBindings(model);
    }).error(function () {
            // todo: add handler
        });
});