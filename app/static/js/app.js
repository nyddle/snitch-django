function SnitchEvent(id, message, type) {
    var self = this;
    self.id = id;
    self.message = message;
    self.type = type;
}

function SnitchEventsViewsModel() {
    var self = this;

    self.filter = ko.observable("all");
    self.events = ko.observableArray();

    self.availableFilters = ko.computed(function () {
        var filters = ["all"];
        self.events().forEach(function (event) {
            if (filters.indexOf(event.type) == -1) {
                filters.push(event.type);
            }
        });
        return filters;
    });

    self.showEvents = ko.computed(function () {
        var type = self.filter();
        if (type === 'all') {
            return self.events();
        }
        $.post('?type=' + type, function (response) {
            self.events([]);
            console.log(response.events);
            self.events(response.events);
        });
    }, self);

    self.checkedEvents = ko.observableArray();

    self.checkEvent = function (event) {

        self.checkedEvents.push(event);
        return true;
    };

    self.removeEvents = function () {
        self.checkedEvents().forEach(function (event) {
            self.events.remove(event);
        });
        self.checkedEvents([]);
    };

    self.applyFilters = function() {
        var data = {
            from: '',
            to: '',
            app: '',
            type: ''
        }
    }
}

$(function () {
    var model = new SnitchEventsViewsModel();
    ko.applyBindings(model);
    $.post('/web/index',function (response) {
        model.events(response.events);
    }).error(function () {
            // todo: add handler
        });
});