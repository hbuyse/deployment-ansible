-- 99-loopback.lua – charge un module-loopback à chaque démarrage
local source_name = "alsa_input.usb-Kingston_HyperX_Virtual_Surround_Sound_00000000-00.analog-stereo"
local sink_name = "alsa_output.usb-Kingston_HyperX_Virtual_Surround_Sound_00000000-00.analog-stereo"
local latency_ms = 30

-- Fonction d’aide pour journaliser de façon claire
local function log(level, msg)
	Log.log(level, "Loopback", msg)
end

-- Vérifie que les deux objets existent avant de charger le module
local function ready()
	log("error", "Hye")

	local source = Session:get_node(source_name)
	local sink = Session:get_node(sink_name)

	if not source then
		log("error", "Source '" .. source_name .. "' introuvable – boucle non créée.")
		return
	end
	if not sink then
		log("error", "Sink '" .. sink_name .. "' introuvable – boucle non créée.")
		return
	end

	return source ~= nil and sink ~= nil
end

-- Callback exécuté dès que le serveur est “ready”
function session_started()
	if not ready() then
		log("error", "Loopback: source ou sink introuvable")
		return
	end

	-- Chargement du module‑loopback de PipeWire (compatible PulseAudio)
	local args = {
		"source=" .. source_name,
		"sink=" .. sink_name,
		"latency_msec=" .. tostring(latency_ms),
	}
	local module = Session:load_module("module-loopback", args)
	if module then
		log("info", "Loopback chargé avec succès")
	else
		log("info", "Échec du chargement du loopback")
	end
end
