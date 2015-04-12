'use strict';

var Colr = require('colr');
var React = require('react');
var ColorPicker = require('react-colorpicker');

var ColorForm = React.createClass({
    propTypes: {
        confirmColorElement: React.PropTypes.func.isRequired,
        initColor: React.PropTypes.string.isRequired,
        initSize: React.PropTypes.number.isRequired,
        del: React.PropTypes.func,
        cancel: React.PropTypes.func.isRequired
    },

    getInitialState: function() {
        return {
            color: this.props.initColor,
            width: this.props.initSize
        };
    },

    handleChange: function(color) {
        this.setState({
            color: color.toHex()
        });
    },

    changeWidth(e) {
        this.setState({
            width: e.target.value
        });
    },

    ok: function() {
        this.props.confirmColorElement(this.state.color, this.state.width);
    },

    render: function() {
        var delbutton;
        if (this.props.del) {
            delbutton = <button onClick={this.props.del}>delete</button>
        } else {
            delbutton = <span />
        }

        return (
            <div className="colorform">
                <ColorPicker
                    color={this.state.color}
                    onChange={this.handleChange}
                />
                <input type="text" value={this.state.width} onChange={this.changeWidth} />{"%"}
                <button onClick={this.ok}>ok</button>
                {delbutton}
                <button onClick={this.props.cancel}>cancel</button>
            </div>
        );
    },
});

var ColorElement = React.createClass({
    propTypes: {
        element: React.PropTypes.shape({
            color: React.PropTypes.string.isRequired,
            width: React.PropTypes.number.isRequired,
            key: React.PropTypes.string.isRequired
        }),
        edit: React.PropTypes.func.isRequired,
        direction: React.PropTypes.string.isRequired
    },

    onEdit() {
        this.props.edit(this.props.element.key);
    },

    render() {
        var title = this.props.element.width + "%: " + this.props.element.color;
        var style = { container: {backgroundColor: this.props.element.color} };

        if(this.props.direction == Direction.Landscape) {
            return (<td width={this.props.element.width * 5} style={style.container} title={title} onClick={this.onEdit}> </td>);

        } else {
            style.container.width = "300px";
            style.container.height = this.props.element.width * 5;
            return (<tr>
                    <td style={style.container} title={title} onClick={this.onEdit}> </td>
                    </tr>);
        }
    }
});

var ColorTable = React.createClass({
    propTypes: {
        colors: React.PropTypes.array.isRequired,
        edit: React.PropTypes.func,
        direction: React.PropTypes.string.isRequired
    },

    render() {
        var colors = this.props.colors.map((c) => {
            return <ColorElement element={c} key={c.key} edit={this.props.edit} direction={this.props.direction} />
        });

        if (this.props.direction == Direction.Landscape) {
            var style = { container: {height:"300px"} };
            return (
                <table>
                    <tbody>
                        <tr style={style.container}>{colors}</tr>
                    </tbody>
                </table>
            );
        } else {
            return (
                <table>
                    <tbody>
                        {colors}
                    </tbody>
                </table>
            );
        }
    }
});

var Direction = {
    Landscape: "landscape",
    Portrait: "portrait"
};

var DirectionRadio = React.createClass({
    propTypes: {
        direction: React.PropTypes.string.isRequired,
        onChange: React.PropTypes.func.isRequired
    },

    render() {
        var isLandscape = this.props.direction == Direction.Landscape;
        return (
            <div>
                <input type={"radio"} name={"direction"} defaultChecked={isLandscape} onChange={this.props.onChange} />Landscape
                <input type={"radio"} name={"direction"} defaultChecked={!isLandscape} onChange={this.props.onChange} />Portrait
            </div>
        );
    }
});

var ColorFormState = {
    Add: 0,
    Edit: 1,
    Unvisible: 2
};

var KantenColors = React.createClass({
    getInitialState() {
        return {
            colorform: ColorFormState.Unvisible,
            colors: [],
            seq: 0,
            direction: Direction.Landscape
        };
    },

    dirChange() {
        var dir = this.state.direction == Direction.Landscape ? Direction.Portrait : Direction.Landscape;
        this.setState({
            direction: dir
        });
    },

    showColorForm(isNew, id) {
        var formState = isNew ? ColorFormState.Add: ColorFormState.Edit;
        this.setState({
            colorform: formState,
            targetkey: id
        });
    },

    showAddForm() {
        this.showColorForm(true);
    },

    showEditForm(id) {
        this.showColorForm(false, id);
    },

    deleteElement() {
        this.setState({
            colors: this.state.colors.filter((c) => this.state.targetkey != c.key),
            colorform: ColorFormState.Unvisible
        });
    },

    cancel() {
        this.setState({
            colorform: ColorFormState.Unvisible
        });
    },

    addElement(color, width) {
        var keyid = 'color' + String(this.state.seq);
        this.state.seq = this.state.seq + 1;

        this.setState({
            colors: this.state.colors.concat({color: color, width: Number(width), key: keyid}),
            colorform: ColorFormState.Unvisible
        }); 
    },

    editElement(color, width) {
        var target = this.state.colors.filter((c) => c.key == this.state.targetkey);
        target.color = color;
        target.width = width;

        this.setState({
            colors: this.state.colors.map((c) => {
                        if (c.key == this.state.targetkey) {
                            return {color: color, width: Number(width), key: this.state.targetkey};
                        } else {
                            return c;
                        }
                    }),
            colorform: ColorFormState.Unvisible
        }); 
    },

    render() {
        var cform;
        if (this.state.colorform == ColorFormState.Add) {
            var color, width, func;
            if (this.state.colors.length == 0) {
                color = "#ffffff";
                width = 100;
            } else {
                c = this.state.colors[this.state.colors.length -1];
                color = c.color;
                width = 100 - this.state.colors.map((c) => c.width).reduce((acc, w) => acc + w); 
            }
            cform = <ColorForm 
                        confirmColorElement={this.addElement} 
                        initColor={color} 
                        initSize={width}
                        cancel={this.cancel}
                    />

        } else if (this.state.colorform == ColorFormState.Edit) {
            var c = this.state.colors.filter((c) => c.key == this.state.targetkey)[0];
            cform = <ColorForm 
                        confirmColorElement={this.editElement}
                        initColor={c.color}
                        initSize={c.width}
                        del={this.deleteElement} 
                        cancel={this.cancel}
                    />

        } else {
            cform = <div />
        }

        var jsncolors = [];
        for(var i=0; i<this.state.colors.length; i++) {
            var dic = this.state.colors[i];
            jsncolors.push({color: dic.color, ratio: dic.width});
        }

        var jsn = JSON.stringify({
            direction: this.state.direction,
            colors: jsncolors
        });

        return (
            <div>
                {cform}        
                <textarea cols={50} rows={5} name={"status"} > #kanten_colors</textarea>
                <br />
                <input type={"button"} onClick={this.showAddForm} value={"add color"} />
                <DirectionRadio direction={this.state.direction} onChange={this.dirChange} />
                <ColorTable colors={this.state.colors} edit={this.showEditForm} direction={this.state.direction} />
                <input type={"hidden"} name={"data"} value={jsn} />
            </div>
        );
    }
});


React.render(React.createFactory(KantenColors)(), document.getElementById('colortable'));
