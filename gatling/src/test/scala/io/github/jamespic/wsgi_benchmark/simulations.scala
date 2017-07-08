package io.github.jamespic.wsgi_benchmark

import scala.concurrent.duration._
import scala.language.postfixOps

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import io.gatling.jdbc.Predef._

object Scenarios {
  val helloWorld = scenario("Hello World")
    .exec(
      http("/hello_world")
      .get("/hello_world")
      .check(bodyString is "Hello World")
    )

  val numericNoGil = scenario("Numeric No GIL")
    .exec(
      http("/numeric_nogil")
      .get("/numeric_nogil")
      .check(status is 200)
    )

  val numericGil = scenario("Numeric GIL")
    .exec(
      http("/numeric_gil")
      .get("/numeric_gil")
      .check(bodyString is "19999999900000000")
    )

  val nativeIO = scenario("Native IO")
    .exec(
      http("/native_io")
      .get("/native_io")
      .check(bodyString is "Success")
    )

  val socketIO = scenario("Socket IO")
    .exec(
      http("/socket_io")
      .get("/socket_io")
      .check(bodyString is "PONG")
    )

  val sendfile = scenario("sendfile")
    .exec(
      http("/sendfile")
      .get("/sendfile")
      .check(md5 is "b6d81b360a5672d80c27430f39153e2c")
    )

  val dynamicFile = scenario("Dynamic File")
    .exec(
      http("/dynamic_file")
      .get("/dynamic_file")
      .check(md5 is "b6d81b360a5672d80c27430f39153e2c")
    )

  val pushWrite = scenario("Push Write")
    .exec(
      http("/push_write")
      .get("/push_write")
      .check(md5 is "b6d81b360a5672d80c27430f39153e2c")
    )

  val sha512 = scenario("SHA-512")
    .exec(
      http("/sha512")
      .post("/sha512")
      .body(ByteArrayBody(Array.fill(1048576)(0.toByte)))
      .check(bodyString is "d6292685b380e338e025b3415a90fe8f9d39a46e7bdba8cb78c50a338cefca741f69e4e46411c32de1afdedfb268e579a51f81ff85e56f55b0ee7c33fe8c25c9")
    )

  val forwardRequest = scenario("Forward Request")
    .exec(
      http("/forward_request")
      .post("/forward_request")
      .body(ByteArrayBody(Array.fill(262144)(0.toByte)))
      .check(bodyString is "Success")
    )

  val gzip = scenario("Gzip")
    .exec(
      http("/gzip")
      .post("/gzip")
      .body(ByteArrayBody(Array.fill(1048576)(0.toByte)))
      .check(sha1 is "480d862eb69d8d083be4391e7472d3018a779ba4")
    )

  val targetHostname = sys.env.getOrElse("TARGET_HOSTNAME", "localhost")
  val httpProtocol = http.baseURL(s"http://${targetHostname}:8765")
}

class HelloWorldSimulation extends Simulation {
  import Scenarios._
  setUp(
    helloWorld.inject(rampUsersPerSec(0.1) to(1000) during(1 minute) randomized)
  ).protocols(httpProtocol)
}

class NumericGilSimulation extends Simulation {
  import Scenarios._
  setUp(
    numericGil.inject(rampUsersPerSec(0.1) to(16) during(1 minute) randomized)
  ).protocols(httpProtocol)
}

class NumericNoGilSimulation extends Simulation {
  import Scenarios._
  setUp(
    numericNoGil.inject(rampUsersPerSec(0.1) to(16) during(1 minute) randomized)
  ).protocols(httpProtocol)
}

class NativeIOSimulation extends Simulation {
  import Scenarios._
  setUp(
    nativeIO.inject(rampUsersPerSec(0.1) to(800) during(1 minute) randomized)
  ).protocols(httpProtocol)
}

class SocketIOSimulation extends Simulation {
  import Scenarios._
  setUp(
    socketIO.inject(rampUsersPerSec(0.1) to(800) during(1 minute) randomized)
  ).protocols(httpProtocol)
}

class PushWriteSimulation extends Simulation {
  import Scenarios._
  setUp(
    pushWrite.inject(rampUsersPerSec(0.1) to(800) during(1 minute) randomized)
  ).protocols(httpProtocol)
}

class DynamicFileSimulation extends Simulation {
  import Scenarios._
  setUp(
    dynamicFile.inject(rampUsersPerSec(0.1) to(800) during(1 minute) randomized)
  ).protocols(httpProtocol)
}

class SendfileSimulation extends Simulation {
  import Scenarios._
  setUp(
    sendfile.inject(rampUsersPerSec(0.1) to(800) during(1 minute) randomized)
  ).protocols(httpProtocol)
}

class SHA512Simulation extends Simulation {
  import Scenarios._
  setUp(
    sha512.inject(rampUsersPerSec(0.1) to(800) during(1 minute) randomized)
  ).protocols(httpProtocol)
}

class ForwardSimulation extends Simulation {
  import Scenarios._
  setUp(
    forwardRequest.inject(rampUsersPerSec(0.1) to(50) during(1 minute) randomized)
  ).protocols(httpProtocol)
}

class GzipSimulation extends Simulation {
  import Scenarios._
  setUp(
    gzip.inject(rampUsersPerSec(0.1) to(400) during(1 minute) randomized)
  ).protocols(httpProtocol)
}
