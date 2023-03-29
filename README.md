<p align="center">
    <img src="./docs/logo.jpg" />
</p>
<p align="center">
    Photo by <a href="https://unsplash.com/@tukacszoltan1984?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Zoltan Tukacs</a> on <a href="https://unsplash.com/s/photos/dog-grass?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
</p>

--------------------------------------------------------------------

# Watchdog for your Chia farm

So you've become a [Chia](https://www.chia.net) farmer and want to maximize the probability of getting a reward? Chiadog
helps with automated monitoring and sends you a mobile notification in case something appears to malfunction.

## Supported Notifications

| Subsystem | Notification (example values) | Priority |
| ------------- | ------------- | ------|
| Harvester | Your harvester appears to be offline! No events for the past 400 seconds. | HIGH |
| Harvester | Disconnected HDD? The total plot count decreased from 100 to 40. | HIGH |
| Harvester | Connected HDD? The total plot count increased from 0 to 42. | LOW |
| Harvester | Experiencing networking issues? Harvester did not participate in any challenge for 120 seconds. It's now working again. | NORMAL |
| Harvester | Seeking plots took too long: 21.42 seconds! | NORMAL |
| Full Node | Experiencing networking issues? Skipped 42 signage points! | NORMAL |
| Full Node | Block found!! | LOW |
| Wallet | Cha-ching! Just received 2.0 XCH ☘️ | LOW |
| Daily Stats | Hello farmer! 👋 Here's what happened in the last 24 hours: <br /><br /> Received ☘️: **2.00** XCH️<br /> Proofs 🧾: **176** found!<br />  - **176** partials submitted 📑<br /> - **0** blocks found 📦<br/> Search 🔍: <br /> - average: **0.46**s <br /> - over 5s: 2 occasions <br /> - over 15s: 1 occasions <br/> Plots 🌱: **42**, new: **2** <br /> Eligible plots 🥇: **0.08** average<br /> Skipped SPs ⚠️: 7 (0.01%) <br /> | LOW |

Please refer to [Status Reference](https://github.com/martomi/chiadog/wiki/Status-Reference) page for detailed
explanations of the notifications.

## How it works?

It parses the `debug.log` generated by the chia process and runs various checks to determine the health of your farmer.
Among others, it can detect if your node has lost sync and the farmer is no longer participating in challenges, or if
one of your external HDDs disconnected and your harvester doesn't have access to the full amount of plots you have.

## Access & Security

It only requires read-access to your `debug.log` file and internet connection to send out notifications. It's highly
recommended that you run `chiadog` in a sandboxed environment. Please use the official [docker image](https://github.com/martomi/chiadog/pkgs/container/chiadog/versions).

Furthermore, following best security practices, you
should [keep your wallet separate](https://github.com/Chia-Network/chia-blockchain/wiki/Good-Security-Practices-on-Many-Machines#keep-your-wallet-separate).

## Supported Integrations for Notifications

You may use one (or more) of the following integrations to receive notifications from `chiadog`.

| Integration | Advantages | Cost |
| ------------- | ------------- | ------|
| [Pushover](https://pushover.net/) | High priority notifications that can override your phone's silent mode. | $5 one time purchase after 30 day trial. |
| [Pushcut](https://pushcut.io/) | Alternative to Pushover |
| E-mail | You probably already have an email. No additional apps. | Free |
| Slack | Quick & easy setup. | Free |
| Discord | Quick & easy setup. | Free |
| Telegram | Quick & easy setup. | Free |
| Shell script (beta) | Execute anything in your own script. | Free |
| MQTT | Well-suited for Home Automation. | Free | 
| Grafana | For hardware monitoring. | Free |
| [Ifttt](https://ifttt.com/) | Can be used to send push notifications or to do other API integrations depending on incoming data. | Free |


For detailed guide on how to test and configure, please refer to [INTEGRATIONS.md](INTEGRATIONS.md).

# Getting started

## Pre-requisites

- Linux, MacOS & Windows
- Python 3.7+
- [Git](https://git-scm.com/downloads)
- Enabled `INFO` logs on your chia farmer

The instructions below are specific to Linux and MacOS, for installing `chiadog` on Windows, please refer to this
separate [README](WINDOWS.md) section.

### How to enable INFO logs on chia farmer?

First configure the log level to `INFO`. This ensures that all logs necessary for chiadog to operate are available
under `~/.chia/mainnet/log/debug.log`.

```
chia configure -log-level=INFO
```

Then restart your farmer to apply the changes:

```
chia start --restart farmer
```

Check that logs are coming in:

```
cat ~/.chia/mainnet/log/debug.log
```

## Installation

### Recommended

The new recommended way of using `chiadog` is via the official [docker image](https://github.com/martomi/chiadog/pkgs/container/chiadog/versions).

### Manual Installation

_For updating from previous version, see section below._

1. Clone the repository

```
git clone https://github.com/martomi/chiadog.git
cd chiadog
```

2. Run the install script.

```
./install.sh
```

3. Copy the example config file

```
cp config-example.yaml config.yaml
```

4. Open up `config.yaml` in your editor and configure it to your preferences. The example is large, feel free to omit any portions where you're fine with the defaults!

### Updating to the latest release

_Skip this if you followed the above section_.

```
cd chiadog

git fetch
git checkout main
git pull

./install.sh
```

## Monitoring a local harvester / farmer

1. Open `config.yaml` and configure `file_log_consumer`:
    - You need to enable the file log consumer to read local chia log files
    - Double-check that the path to your chia logs is correct

2. Start the watchdog

```
./start.sh
```

3. Verify that your plots are detected. Within a few seconds you should see INFO log:

```
Detected new plots. Farming with 42 plots.
```

If you see the above log message, you can be certain that `chiadog` is running correctly. It'll remain silent until the
next scheduled daily notification or until any issues are detected.

You can repeat the above process for every machine where you are running a harvester. Use
the `notification_title_prefix`
in `config.yaml` to give every machine a unique notification prefix so that you can easily distinguish them.

If you don't want to setup `chiadog` on each machine separately, you can also monitor multiple remote harvesters and run
chiadog on a single machine. Please refer to the wiki page
on [Remote Monitoring Multiple Harvesters](https://github.com/martomi/chiadog/wiki/Monitoring-Multiple-Harvesters).

## Troubleshooting

You can enable more verbose logging from `config.yaml` by changing `INFO` to `DEBUG`. You should see logs for every
keep-alive event from the harvester.

### Times are wrong?

Chia has not yet introduced timezone aware log timestamps. Until they do make sure the `TZ` environment variable matches 
between the machine producing the logs and running chiadog. If running chiadog on Docker, pass in `-e TZ=UTC`, substituting
`UTC` with your timezone, for example `Europe/London`.

# Advanced Usage

## Redundant monitoring for `chiadog`

There are failure-cases in which `chiadog` is helpless. For example, your computer completely freezes or shuts down.
Perhaps your entire home network goes down. `chiadog` won't be able to send you a notification.

There's a way however: in the [config](config-example.yaml) under the section of `keep_alive_monitor`, you can enable
pinging to a remote service that will act as a watchdog of `chiadog`. A second level of redundancy, if you wish!

You may chose your favourite service for that, I've tested it with
[HealthChecks.io](https://healthchecks.io). It's free to signup and create an endpoint that expects to receive pings
every 10 minutes. If it does not, it will notify you. It has integrations with Pushover, Email, Slack, Discord and more.

## Running `chiadog` in the background

```
. ./venv/bin/activate
nohup python3 -u main.py --config config.yaml > output.log 2>&1 &
```

To stop chiadog, you can find the Process ID (PID) via `ps aux | grep main.py` and then softly interrupt the process
with `kill -SIGINT <pid_here>`.

## Running `chiadog` as sandboxed systemd service

Alternatively to the original chiadog docker image, you can setup a [systemd service](scripts/linux/chiadog.service)
which runs chiadog as a limited user and blocks access to key chia locations.

# Contributing

Contributions are always welcome! Please refer to [CONTRIBUTING](CONTRIBUTING.md) documentation.
