// rent_a_relic_market.js
/**
 * Rent-a-Relic Market — Book Authenticated Vintage Compute
 * Mongoose/Node.js implementation for booking vintage hardware sessions.
 *
 * Bounty: #2312 (150 RTC)
 * PoA-Signature: poa_8BsByR6rPqxDPku6dYtdoiSk6bdgE9YETbLQF2RGSw1C
 */

const mongoose = require('mongoose');
const crypto = require('crypto');

const relicSchema = new mongoose.Schema({
  hardwareId: { type: String, required: true, unique: true },
  model: { type: String, required: true },
  year: { type: Number, required: true },
  owner: { type: String, required: true },
  status: { type: String, enum: ['available', 'booked', 'maintenance'], default: 'available' },
  authenticationHash: { type: String, required: true },
  hourlyRateRTC: { type: Number, default: 5 }
});

const bookingSchema = new mongoose.Schema({
  relic: { type: mongoose.Schema.Types.ObjectId, ref: 'Relic', required: true },
  user: { type: String, required: true },
  startTime: { type: Date, default: Date.now },
  durationHours: { type: Number, required: true },
  totalCostRTC: { type: Number, required: true },
  sessionToken: { type: String, required: true }
});

const Relic = mongoose.model('Relic', relicSchema);
const Booking = mongoose.model('Booking', bookingSchema);

async function registerRelic(hardwareId, model, year, owner, rawSecret) {
  const authHash = crypto.createHash('sha256').update(rawSecret).digest('hex');
  return await new Relic({ hardwareId, model, year, owner, authenticationHash: authHash }).save();
}

async function bookSession(hardwareId, user, hours) {
  const relic = await Relic.findOne({ hardwareId, status: 'available' });
  if (!relic) throw new Error('Relic not available for booking.');
  const totalCost = relic.hourlyRateRTC * hours;
  const sessionToken = crypto.randomBytes(32).toString('hex');
  const booking = new Booking({ relic: relic._id, user, durationHours: hours, totalCostRTC: totalCost, sessionToken });
  relic.status = 'booked';
  await relic.save();
  return await booking.save();
}

module.exports = { Relic, Booking, registerRelic, bookSession };
