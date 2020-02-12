import React, { Component } from "react";
import {
  Modal,
  Image,
  View,
  StyleSheet,
  Button,
  Alert,
  Text,
  Dimensions,
  TouchableOpacity
} from "react-native";
import MapView, {
  PROVIDER_GOOGLE,
  MAP_TYPES,
  Marker,
  Polygon,
  ProviderPropType
} from "react-native-maps";
import { fetchVehicle } from "./api";
import RNEventSource from "react-native-event-source";
import { Overlay } from "react-native-elements";
import NumericInput from "react-native-numeric-input";

const { width, height } = Dimensions.get("window");

const ASPECT_RATIO = width / height;
const LATITUDE = 37.78825;
const LONGITUDE = -122.4324;
const LATITUDE_DELTA = 0.0922;
const LONGITUDE_DELTA = LATITUDE_DELTA * ASPECT_RATIO;
let id = 0;

let Drone_speed = 0;
let Altitude = 0;
let Bf_distance = 0;

const ip_adress = "http://10.1.34.172";

export default class drone_app extends Component {
  constructor(props) {
    super(props);

    this.state = {
      region: {
        latitude: LATITUDE,
        longitude: LONGITUDE,
        latitudeDelta: LATITUDE_DELTA,
        longitudeDelta: LONGITUDE_DELTA
      },
      region1: {
        latitude: LATITUDE,
        longitude: LONGITUDE,
        latitudeDelta: LATITUDE_DELTA,
        longitudeDelta: LONGITUDE_DELTA
      },
      polygon: null,
      editing: null,
      drone_data: null,
      isVisible: false
    };
  }

  finish() {
    this.setState({
      polygon: this.state.editing,
      editing: null
    });
  }

  start() {
    if (!this.state.polygon) {
      alert("Please select an area of 4 points!");
    } else if (this.state.polygon.coordinates.length == 4) {
      fetch(ip_adress + ":8080/post/", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify(this.state.polygon.coordinates)
      });
    } else alert("cordinate error (must be 4) !!");
  }
  onPress(e) {
    const { editing } = this.state;
    if (!editing) {
      this.setState({
        editing: {
          id: id++,
          coordinates: [e.nativeEvent.coordinate]
        }
      });
    } else {
      this.setState({
        editing: {
          ...editing,
          coordinates: [...editing.coordinates, e.nativeEvent.coordinate]
        }
      });
    }
  }

  async getData() {
    let dat = await fetchVehicle();
    this.setState({ data: dat[0] }, () => console.warn(dat));
  }

  componentDidMount() {
    this.eventSource = new RNEventSource(
      ip_adress + ":3000/.well-known/mercure?topic=drone"
    );

    // Grab all events with the type of 'message'
    this.eventSource.addEventListener("message", data => {
      //  console.log(data.type); // message
      this.setState({ drone_data: JSON.parse(data.data)[0].fields });
      this.setState({
        region: {
          latitude: this.state.drone_data.lat,
          longitude: this.state.drone_data.longt,
          latitudeDelta: LATITUDE_DELTA,
          longitudeDelta: LONGITUDE_DELTA
        }
      });
      console.log(JSON.parse(data.data)[0].fields);
    });
    console.log("Mount");
  }

  componentWillUnmount() {
    this.eventSource.removeAllListeners();
    this.eventSource.close();
    console.log("UnMount");
  }

  render() {
    const mapOptions = {
      scrollEnabled: true
    };

    if (this.state.editing) {
      mapOptions.scrollEnabled = false;
      mapOptions.onPanDrag = e => this.onPress(e);
    }

    return (
      <View style={styles.container1}>
        <View style={styles.backgroundContainer}>
          <View
            style={{ width: "150%", height: 45, backgroundColor: "#62d1aa" }}
          />
        </View>
        <View style={{ flexDirection: "row" }}>
          <Image
            style={{ width: 45, height: 45, marginLeft: "1%" }}
            source={require("./img/Logo.png")}
          />
          <TouchableOpacity
            style={{ width: 45, height: 45 }}
            onPress={() => this.setState({ isVisible: true })}
          >
            <Image
              source={require("./img/Params.png")}
              style={{ width: 40, height: 45 }}
            />
          </TouchableOpacity>
        </View>
        <View style={styles.connect}>
          <Button
            title="Connect"
            onPress={() =>
              fetch(ip_adress + ":8080/post/", {
                method: "POST",
                headers: {
                  Accept: "application/json",
                  "Content-Type": "application/json"
                },
                body: JSON.stringify({ a: 1, b: "Textual content" })
              })
            }
          ></Button>
        </View>
        <View style={styles.finish}>
          <Button
            title="Select"
            onPress={() => this.finish()}
            style={[styles.bubble, styles.button]}
          ></Button>
        </View>

        <View style={styles.start}>
          <Button
            title="Upload"
            onPress={() => this.start()}
            style={[styles.bubble, styles.button]}
          ></Button>
        </View>
        <MapView
          provider={this.props.provider}
          style={styles.map}
          mapType={MAP_TYPES.HYBRID}
          //inisialregion= {this.state.region1}
          camera={{
            center: {
              latitude: this.state.region1.latitude,
              longitude: this.state.region1.longitude
            },
            pitch: 1,
            heading: 2,
            altitude: 5,
            zoom: 16
          }}
          onPress={e => this.onPress(e)}
          {...mapOptions}
        >
          <Marker
            coordinate={{
              latitude: this.state.region.latitude,
              longitude: this.state.region.longitude
            }}
          ></Marker>
          {this.state.polygon && (
            <Polygon
              key={this.state.polygon.id}
              coordinates={this.state.polygon.coordinates}
              strokeColor="#000"
              fillColor="rgba(255,0,0,0.5)"
              strokeWidth={2}
            />
          )}
          {this.state.editing && (
            <Polygon
              key={this.state.editing.id}
              coordinates={this.state.editing.coordinates}
              holes={this.state.editing.holes}
              strokeColor="#000"
              fillColor="rgba(255,0,0,0.5)"
              strokeWidth={1}
            />
          )}
        </MapView>
        {this.state.drone_data && (
          <TouchableOpacity style={styles.bubble}>
            <Text>Armed: {this.state.drone_data.arm}</Text>
            <Text>Mode: {this.state.drone_data.mode}</Text>
            <Text>Altitude: {this.state.drone_data.alt}</Text>
            <Text>
              Battery:
              {this.state.drone_data.battery.split(",")[2].split("=")[1]}%
            </Text>
          </TouchableOpacity>
        )}
        <TouchableOpacity
          style={{
            backgroundColor: "rgba(255,255,255,0.7)",
            paddingHorizontal: 5,
            paddingVertical: 5,
            borderRadius: 15,
            position: "absolute",
            bottom: 7,
            right: 5
          }}
          onPress={() => {
            if (this.state.drone_data)
              this.setState({
                region1: {
                  latitude: this.state.drone_data.lat,
                  longitude: this.state.drone_data.longt,
                  latitudeDelta: LATITUDE_DELTA,
                  longitudeDelta: LONGITUDE_DELTA
                }
              });
          }}
        >
          <Image
            source={require("./img/get_position.png")}
            style={{ width: 40, height: 40 }}
          ></Image>
        </TouchableOpacity>
        <View>
          <Overlay
            isVisible={this.state.isVisible}
            width={"90%"}
            height={"90%"}
          >
            <View
              style={{
                flex: 1,
                flexDirection: "column",
                justifyContent: "space-between"
              }}
            >
              <View
                style={{
                  width: "50%",
                  flexDirection: "row",
                  justifyContent: "center",
                  alignItems: "center"
                }}
              >
                <View style={{ width: "50%" }}>
                  <Text>Drone speed m/s:</Text>
                </View>
                <View style={{}}>
                  <NumericInput
                    onChange={value => (Drone_speed = value)}
                    initValue={Drone_speed}
                    minValue={0}
                    totalWidth={70}
                    totalHeight={40}
                  />
                </View>
              </View>

              <View
                style={{
                  width: "50%",
                  flexDirection: "row",
                  justifyContent: "center",
                  alignItems: "center"
                }}
              >
                <View style={{ width: "50%" }}>
                  <Text>Altitude m:</Text>
                </View>
                <NumericInput
                  onChange={value => (Altitude = value)}
                  initValue={Altitude}
                  minValue={0}
                  totalWidth={70}
                  totalHeight={40}
                />
              </View>

              <View
                style={{
                  width: "50%",
                  flexDirection: "row",
                  justifyContent: "center",
                  alignItems: "center"
                }}
              >
                <View style={{ width: "50%" }}>
                  <Text>Distance between back and forth m:</Text>
                </View>
                <NumericInput
                  onChange={value => (Bf_distance = value)}
                  initValue={Bf_distance}
                  minValue={0}
                  totalWidth={70}
                  totalHeight={40}
                />
              </View>

              <View
                style={{
                  justifyContent: "center",
                  alignItems: "center",
                  alignContent: "center"
                }}
              >
                <Button
                  title="Save parameters"
                  onPress={() => this.setState({ isVisible: false })}
                />
              </View>
            </View>
          </Overlay>
        </View>
      </View>
    );
  }
}

drone_app.propTypes = {
  provider: ProviderPropType
};

var styles = StyleSheet.create({
  backgroundContainer: {
    position: "absolute",
    top: 0,
    bottom: 0,
    left: 0,
    right: 0
  },
  container1: {
    flex: 1
  },
  connect: {
    position: "absolute",
    top: 5,
    right: 5,
    width: 100,
    alignSelf: "flex-end"
  },
  container: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: "flex-end",
    alignItems: "center"
  },
  map: {
    height: "100%"
    //...StyleSheet.absoluteFillObject,
  },
  bubble: {
    backgroundColor: "rgba(255,255,255,0.7)",
    paddingHorizontal: 12,
    paddingVertical: 12,
    borderRadius: 5,
    position: "absolute",
    top: 50,
    right: 3
  },
  latlng: {
    width: 200,
    alignItems: "stretch"
  },
  button: {
    width: 80,
    paddingHorizontal: 12,
    alignItems: "center",
    marginHorizontal: 10
  },
  buttonContainer: {
    // flexDirection: 'row',
    marginVertical: 20,
    backgroundColor: "transparent"
  },
  finish: {
    position: "absolute",
    top: 5,
    right: 110,
    width: 100,
    flexDirection: "row-reverse"
  },
  start: {
    position: "absolute",
    top: 5,
    right: 180,
    width: 100,
    flexDirection: "row-reverse"
  }
});
