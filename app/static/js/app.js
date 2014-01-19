function SnitchEvent(id, message, type, app, timestamp) {
    var self = this;
    self.id = id;
    self.message = message;
    self.type = type;
    self.app = app;
    self.timestamp = timestamp;
    self.checked = false;
}

function SnitchEventsViewsModel() {
    var self = this;

    self.filterType = ko.observable("all");
    self.dateFrom = ko.observable();
    self.dateTo = ko.observable();

    self.apps = ko.observableArray(['Default App']);
    self.currentApps = ko.observableArray(self.apps());

    self.events = ko.observableArray([]);
    self.checkedEvents = ko.observableArray([]);

    self.showFormControls = ko.observable(false);

    self.checkedEvents.subscribe(function () {
        if (self.checkedEvents().length > 0) {
            self.showFormControls(true);
        } else {
            self.showFormControls(false);
        }
    });

    self.availableTypes = ko.computed(function () {
        var filters = ["all"];
        self.events().forEach(function (event) {
            if (filters.indexOf(event.type) == -1) {
                filters.push(event.type);
            }
        });
        return filters;
    });

    self.showEvents = ko.computed(function () {
        var type = self.filterType();
        if (type === 'all') {
            return self.events();
        }
        $.post('?type=' + type, function (response) {
            self.events([]);
            self.events(response.events);
        });
    }, self);

    self.clickOnApp = function (data, event) {

        var index = self.currentApps.indexOf(data),
            elem = $(event.target);
        if (index > -1) {
            self.currentApps.remove(data);
        } else {
            self.currentApps.push(data);
        }
        elem.toggleClass('btn-primary').toggleClass('btn-default');
        self.currentApps.valueHasMutated();
        return false;
    }

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

    self.applyFilters = function () {
        var data = [
            self.dateFrom() ? 'from='+self.dateFrom() : '',
            self.dateTo() ? 'to='+self.dateTo() : '',
            self.apps() ? 'apps='+self.apps() : '',
            self.filterType() ? 'type='+self.filterType() : ''
        ]

        alert('Applied!');
        return true;
    }
}

$(function () {
    var model = new SnitchEventsViewsModel();

    $('.datepicker1').datepicker();
    $('.datepicker2').datepicker();
    $.post('/web/index',function (response) {
        for (var i = 0; i < response.events.length; i++) {
            var event = response.events[i];
            model.events.push(new SnitchEvent(1, event.message, event.type, event.app, event.timestamp));
        }
        // todo: add response.apps
        ko.applyBindings(model);
    }).error(function () {
            // todo: add handler
        });
});